import requests

from pyrecorder import record


#@record
def make_https_requests():
    response = requests.get('https://google.com')
    response.raise_for_status()
    print(response.content)


make_https_requests()
