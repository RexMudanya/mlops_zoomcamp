import json
import base64
import boto3
import os
import mlflow

TEST_RUN = os.getenv('DRY_RUN', 'Flse') == 'True'
PREDICTIONS_STREAM_NAME = os.getenv('PREDICTIONS_STREAM_NAME', 'ride_predictions')
# RUN_ID = os.getenv('RUN_ID')

logged_model = f"s3://mlflow-artifacts-remote-store-artifacts/lin_reg.bin"
model = mlflow.pyfunc.load_model(logged_model)

kinesis_client = boto3.client('kinesis')

def prepare_features(ride):
    features = {}
    features['PU_DO'] = '%s_%s' % (ride["PULocationID"], ride["DOLocationID"])
    features["trip_distance"] = ride["trip_distance"]
    return features

def predict(features):
    # X = dv.transform(feature)
    # preds = model.predict(X)
    pred = model.predict(features)
    return float(pred[0])


def lambda_handler(event, context):
    predictions = []
    for record in event['Records']:
        encoded_data = record['kinesis']['data']
        decoded_data = base64.b64decode(encoded_data).decode('utf-8')
        ride_event = json.loads(decoded_data)
        # print(ride_event)
        ride = ride_event['ride']
        ride_id = ride_event['ride_id']
        
        features = prepare_features(ride)
        prediction = predict(features)
        prediction_event = {
            'model': 'ride_duration_prediction_model',
            'version': '123',
            'prediction': {
                'ride_duration': prediction,
                'ride_id': ride_id
            }
        }
        
        if not TEST_RUN:
            kinesis_client.put_record(
                StreamName = PREDICTIONS_STREAM_NAME,
                Data=json.dumps(prediction_event),
                PartitionKey=str(ride_id)
                )
        
        predictions.append(prediction_event)
        
    return {
        'predictions': predictions
    }
 