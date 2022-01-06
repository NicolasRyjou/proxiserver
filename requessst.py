import requests

payload = {
    "lat":12,
    "lng":11,
    "max_radius":15
}

print(requests.get('http://127.0.0.1:5000/api/get-chats-near-me', params=payload))