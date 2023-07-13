import os
import json
import base64

import boto3
import mlflow


def get_model_location(run_id):
    model_location = os.getenv("MODEL_LOCATION")

    if model_location is not None:
        return model_location

    model_bucket = os.getenv("MODEL_BUCKET", "mlflow-models")
    experiment_id = os.getenv("MLFLOW_EXPERIMENT_ID", "1")
    model_location = f"s3://{model_bucket}/{experiment_id}/{run_id}/artifacts/model"
    return model_location


def load_model(run_id):
    model_path = get_model_location(run_id)
    model = mlflow.pyfunc.load_model(model_path)
    return model


def base64_decode(encoded_data):
    decoded_data = base64.b64decode(encoded_data).decode("utf-8")
    ride_event = json.loads(decoded_data)

    return ride_event


class ModelService:
    def __init__(self, model, model_version=None, callbacks=None) -> None:
        self.model = model
        self.model_version = model_version
        self.callbacks = callbacks or []

    def prepare_features(self, ride):
        features = {}
        features["PU_DO"] = f'{ride["PULocationID"]}_{ride["DOLocationID"]}'
        features["trip_distance"] = ride["trip_distance"]
        return features

    def predict(self, features):
        # X = dv.transform(feature)
        # preds = model.predict(X)
        pred = self.model.predict(features)
        return float(pred[0])

    def lambda_handler(self, event, context):
        predictions = []
        for record in event["Records"]:
            encoded_data = record["kinesis"]["data"]
            ride_event = base64_decode(encoded_data)
            # print(ride_event)
            ride = ride_event["ride"]
            ride_id = ride_event["ride_id"]

            features = self.prepare_features(ride)
            prediction = self.predict(features)
            prediction_event = {
                "model": "ride_duration_prediction_model",
                "version": self.model_version,
                "prediction": {"ride_duration": prediction, "ride_id": ride_id},
            }
            for callback in self.callbacks:
                callback(prediction_event)

            predictions.append(prediction_event)

        return {"predictions": predictions}


class KinesisCallback:
    # pylint: disable=too-few-public-methods
    def __init__(self, kinesis_client, PREDICTIONS_STREAM_NAME) -> None:
        self.kinesis_client = kinesis_client
        self.PREDICTIONS_STREAM_NAME = PREDICTIONS_STREAM_NAME

    def put_record(self, prediction_event):
        ride_id = prediction_event["prediction"]["ride_id"]
        self.kinesis_client.put_record(
            StreamName=self.PREDICTIONS_STREAM_NAME,
            Data=json.dumps(prediction_event),
            PartitionKey=str(ride_id),
        )


def create_kinesis_client():
    endpoint_url = os.getenv("KINESIS_ENDPOINT_URL")
    if endpoint_url is None:
        return boto3.client("kinesis")

    return boto3.client("kinesis", endpoint_url=endpoint_url)


def init(prediction_stream_name: str, run_id: str, test_run: bool):
    model = load_model(run_id)
    callbacks = []
    if not test_run:
        kinesis_client = create_kinesis_client()
        KinesisCallback = KinesisCallback(kinesis_client, prediction_stream_name)
        callbacks.append(KinesisCallback.put_record)
    model_service = ModelService(model, model_version=run_id, callbacks=callbacks)
    return model_service
