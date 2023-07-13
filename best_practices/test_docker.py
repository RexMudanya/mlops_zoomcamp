# pylint: disable=duplicate-code
import requests
import json

from deepdiff import Deepdiff

event = json.load(open('event.json', 'rt', encoding='utf-8'))


url = 'http://localhost:8080/2015-03-31/functions/function/invocations'
actual_response = requests.post(url, json=event).json()
print('Actual Response')
print(json.dumps(actual_response, indent=2))
expected_response = {
    [ {
                'model': 'ride_duration_prediction_model',
                'version': "test123",
                'prediction': {
                    'ride_duration': 10,
                    'ride_id': 256
                }
            }]
}

diff = Deepdiff(actual_response, expected_response, significant_digits=1 )

assert 'type_changes' not in diff
assert 'values_changed' not in diff
