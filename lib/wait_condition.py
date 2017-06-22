import json

import requests
import datetime

import settings


def report_success(my_settings: settings.Settings, reason: str):
    return report_status(my_settings, reason, "SUCCESS")


def report_failure(my_settings: settings.Settings, reason: str):
    return report_status(my_settings, reason, "FAILURE")


def report_status(my_settings: settings.Settings, reason: str, status: str):
    response_url_full = my_settings.pcf_pcfwaithandle
    response_url, response_params = response_url_full.split('?')
    response_for_waitcondition = build_payload(reason, status)

    print("Writing to wait handle {}".format(response_url_full))
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
