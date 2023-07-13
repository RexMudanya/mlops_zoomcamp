import os

import model

TEST_RUN = os.getenv("DRY_RUN", "False") == "True"
PREDICTIONS_STREAM_NAME = os.getenv("PREDICTIONS_STREAM_NAME", "ride_predictions")

model_service = model.init(
    prediction_stream_name=PREDICTIONS_STREAM_NAME,
    RUN_ID=os.getenv("RUN_ID"),
    test_run=TEST_RUN,
)


def lambda_handler(event, context):
    # pylint: disable=unused-argument
    return model_service.lambda_handler(event)
