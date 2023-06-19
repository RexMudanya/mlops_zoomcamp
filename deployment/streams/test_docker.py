import requests

event = {}

url = ''
response = requests.post(url, json=event)
print(response.json())
