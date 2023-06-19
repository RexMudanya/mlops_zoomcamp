import lambda_function

event = {
    "ride": {
        "PULocationID": 130,
        "DOLocationID": 205,
        "trip_distance": 3.66
    },
    "ride_id": 256
}

result = lambda_function.lambda_handler(event, None)
print(result)
