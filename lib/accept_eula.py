import enum
import json
import time

import requests

import settings

max_retries = 5


def exponential_backoff(my_settings: settings.Settings, release_id: int, attempt=0):
    result = post_eula(my_settings, release_id)
    if result != EULAResult.SUCCESS:
        if result == EULAResult.RETRY and attempt < max_retries:
            print("Retrying, {}".format(attempt))
            time.sleep(attempt ** 3)
            result = exponential_backoff(my_settings, attempt + 1)

    return result


def accept_ert_eula(my_settings: settings.Settings):
    release_id = get_release_id()
    result = exponential_backoff(my_settings, release_id)
    if result == EULAResult.SUCCESS:
        return 0
    else:
        return 1


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
        return EULAResult.SUCCESS
    elif response.status_code >= 500:
        return EULAResult.RETRY
    return EULAResult.FAILURE


def get_release_id():
    with open('/home/ubuntu/tiles/ert-metadata.json', 'r') as metadata_file:
        metadata = json.loads(metadata_file.read())

    return metadata["Release"]["ID"]
