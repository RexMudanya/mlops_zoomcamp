from pathlib import Path

import model


def read_text(file):
    test_directory = Path(__file__).parent
    with open(test_directory / file, "rt", encoding="utf-8") as f_in:
        return f_in.read().strip()


def test_base64_decode():
    base_input = read_text("data.b64")
    actual_result = model.base64_decode(base_input)
    expected_result = {}
    assert actual_result == expected_result


def test_prepare_features():
    model_service = model.ModelService(None)
    ride = {"PULocationID": 130, "DOLocationID": 205, "trip_distance": 3.66}

    actual_features = model_service.prepare_features(ride)

    expected_features = {"PU_DO": "130_205", "trip_distance": 3.66}

    assert actual_features == expected_features


class ModelMock:
    def __init__(self, value) -> None:
        self.value = value

    def predict(self, X):
        n = len(X)
        return [self.value] * n


def test_predict():
    model_mock = ModelMock(10)
    model_service = model.ModelService(model_mock)
    features = {"PU_DO": "130_205", "trip_distance": 3.66}
    actual_prediction = model_service.predict(features)
    expected_prediction = 10

    assert actual_prediction == expected_prediction


def test_lambda_handler():
    model_mock = ModelMock(10)
    model_version = "test123"
    model_service = model.ModelService(model_mock, model_version)
    base64_input = read_text("data.b64")
    event = {
        "Records": [
            {
                "kinesis": {
                    "data": base64_input,
                    "approximateArrivalTimestamp": 1654161514.132,
                },
            }
        ]
    }
    actual_predictions = model_service.lambda_handler(event)
    expected_predictions = [
        {
            "model": "ride_duration_prediction_model",
            "version": model_version,
            "prediction": {"ride_duration": 10, "ride_id": 256},
        }
    ]
    assert actual_predictions == expected_predictions
