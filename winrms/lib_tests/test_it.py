import requests

__author__ = 'ubuntu'

response = requests.get('http://localhost:8000/service_info?service_name=skypeupdate')

print response.text