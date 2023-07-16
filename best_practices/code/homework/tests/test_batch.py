import batch

import pandas as pd
from datetime import datetime


def dt(hour, minute, second=0):
    return datetime(2022, 1, 1, hour, minute, second)


def test_prepare_data():
    data = [
        (None, None, dt(1, 2), dt(1, 10)),
        (1, None, dt(1, 2), dt(1, 10)),
        (1, 2, dt(2, 2), dt(2, 3)),
        (None, 1, dt(1, 2, 0), dt(1, 2, 50)),
        (2, 3, dt(1, 2, 0), dt(1, 2, 59)),
        (3, 4, dt(1, 2, 0), dt(2, 2, 1)),     
    ]

    columns = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']
    df = pd.DataFrame(data, columns=columns)

    expected_output = {'PULocationID': {0: '-1', 1: '1', 2: '1'},
                 'DOLocationID': {0: '-1', 1: '-1', 2: '2'},
                 'tpep_pickup_datetime': {0: '1640998920000000000',
                  1: '1640998920000000000',
                  2: '1641002520000000000'},
                 'tpep_dropoff_datetime': {0: '1640999400000000000',
                  1: '1640999400000000000',
                  2: '1641002580000000000'},
                 'duration': {0: 8.0, 1: 8.0, 2: 1.0}}

    predicted_output = batch.prepare_data(df, columns)
    print(predicted_output.shape)

    assert predicted_output.to_dict() == expected_output
