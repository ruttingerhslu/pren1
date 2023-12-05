import requests
import json

from pixel_detection.constants import *


def send_cube_configuration_to_server(configuration):

    data = json.dumps(configuration)
    print(f"Requestbody sent to Server: {data}")

    response = requests.post(url, headers=headers, data=data)
    print(response)
    print(f"Response Content: {response.content}")
    return response

