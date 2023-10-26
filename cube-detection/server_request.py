import requests
import datetime

# URL to send the json for validation
url_team09 = 'http://18.192.48.168:5000/cubes/team09'


def validateSetup(body):
    r = requests.post(url_team09, body)

    print(r.status_code)

def buildBody():
    # Build Json RequestBody
    return {
        "time": datetime.now(),
        "config": {
            "1": "red",
            "2": "blue",
            "3": "red",
            "4": "yellow",
            "5": "",
            "6": "",
            "7": "yellow",
            "8": "red"
        }
    }


body = buildBody()
validateSetup(body)
