import requests
import json

from pixel_detection.constants import *


def send_cube_configuration_to_server(configuration):
    """
    Send the detected cube configuration to the provided HTTP test server.

    Parameters:
    - configuration (dict): The detected cube configuration.

    Returns:
    - response (Response object): The HTTP response from the server.
    """

    # Die Konfiguration als JSON konvertieren.
    data = json.dumps(configuration)
    print(f"Requestbody sent to Server: {data}")

    # Die Daten an den Server senden und die Antwort erhalten.
    response = requests.post(url, headers=headers, data=data)
    print(response)
    print(f"Response Content: {response.content}")

    return response

