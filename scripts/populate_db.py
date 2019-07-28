import requests

BASE_URL = "http://localhost:5000"

user = requests.post(
    BASE_URL + "/api/user",
    json={"name": "[Your username]"}
).json()

actions = [
    "Action 1",
    "Action 2",
    "Action 3",
]

for action in actions:
    requests.post(
        BASE_URL + "/api/action",
        json={"name": action}
    )
