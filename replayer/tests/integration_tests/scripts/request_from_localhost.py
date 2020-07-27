import requests

from pyrecorder import record


@record
def make_request():
    response = requests.get('http://localhost:8000/ping')
    response.raise_for_status()
    assert response.content == b'pong', f"Response content was {response.content}"


make_request()
