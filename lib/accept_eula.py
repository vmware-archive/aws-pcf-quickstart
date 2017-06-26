import enum
import json
import time

import requests

import settings

max_retries = 5


def exponential_backoff(my_settings: settings.Settings, release_id: int, attempt=0):
    response, result = post_eula(my_settings, release_id)
    if result != EULAResult.SUCCESS:
        if result == EULAResult.RETRY and attempt < max_retries:
            print("Retrying, {}".format(attempt))
            time.sleep(attempt ** 3)
            response, exponential_backoff(my_settings, attempt + 1)

    return response, result


def accept_ert_eula(my_settings: settings.Settings):
    release_id = get_release_id()
    response, result = exponential_backoff(my_settings, release_id)
    if result == EULAResult.SUCCESS:
        return "Success", "", 0
    else:
        return "Failed to accept EULA; status code from Pivotal Network {}".format(response.status_code), "", 1

class EULAResult(enum.Enum):
    SUCCESS = 0,
    FAILURE = 1,
    RETRY = 2


def post_eula(my_settings: settings.Settings, release_id: int):
    response = requests.post(
        url='https://network.pivotal.io/api/v2/products/elastic-runtime/releases/{}/eula_acceptance'.format(release_id),
        headers={
            'Authorization': 'Token {}'.format(my_settings.pcf_input_pivnettoken),
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'PCF-Ecosystem-AWS-client'
        }
    )
    print(response)
    if response.status_code < 300:
        return response, EULAResult.SUCCESS
    elif response.status_code >= 500:
        return response, EULAResult.RETRY
    return response, EULAResult.FAILURE


def get_release_id():
    with open('/home/ubuntu/tiles/ert-metadata.json', 'r') as metadata_file:
        metadata = json.loads(metadata_file.read())

    return metadata["Release"]["ID"]
