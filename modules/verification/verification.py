import requests
import json

from constants.constants import *


def send_cube_configuration_to_server(configuration):

    data = json.dumps(configuration)
    print(f"Requestbody sent to Server: {data}")

    response = requests.post(url + "/config", headers=headers, data=data)
    print(response)
    print(f"Response Content: {response.content}")
    return response


def send_end_signal_to_server():
    response = requests.post(url + "/end", headers=headers)
    print(response)
    print(f"Response Content: {response.content}")
    return response


def send_start_signal_to_server():
    response = requests.post(url + "/start", headers=headers)
    print(response)
    print(f"Response Content: {response.content}")
    return response

