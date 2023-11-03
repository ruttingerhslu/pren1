import requests
import json

def send_cube_configuration_to_server(configuration):
    """
    Send the detected cube configuration to the provided HTTP test server.

    Parameters:
    - configuration (dict): The detected cube configuration.

    Returns:
    - response (Response object): The HTTP response from the server.
    """
    # Die URL des Testservers und des gewünschten Endpunkts.
    base_url = "http://18.192.48.168:5000"
    endpoint = "/cubes/team09"
    url = base_url + endpoint

    # Den Header für die HTTP-Anfrage setzen.
    headers = {
        "Content-Type": "application/json"
    }

    # Die Konfiguration als JSON konvertieren.
    data = json.dumps(configuration)

    # Die Daten an den Server senden und die Antwort erhalten.
    response = requests.post(url, headers=headers, data=data)

    return response

