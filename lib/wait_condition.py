import json

import requests
import datetime

import settings


def report_success(my_settings: settings.Settings, reason: str):
    report_status(my_settings, reason, "SUCCESS")


def report_failure(my_settings: settings.Settings, reason: str):
    report_status(my_settings, reason, "FAILURE")


def report_status(my_settings: settings.Settings, reason: str, status: str):
    # todo: read from settings
    with open('/var/local/cloudformation/faster.txt', 'r') as file:
        response_url_full = file.read().strip()

    response_url, response_params = response_url_full.split('?')
    print("---------------------")
    print(response_url)
    print(response_params)
    print("-------------------------")
    response_for_waitcondition = build_payload(reason, status)
    response = requests.put(
        url=response_url, params=response_params,
        data=str.encode(json.dumps(response_for_waitcondition))
    )

    print(response)

    return 0


def build_payload(reason, status):
    return {
        "Status": status,
        "UniqueId": "ID{}".format(int(datetime.datetime.now().timestamp())),
        "Data": reason,
        "Reason": reason
    }
