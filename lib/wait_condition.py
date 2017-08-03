# aws-pcf-quickstart
#
# Copyright (c) 2017-Present Pivotal Software, Inc. All Rights Reserved.
#
# This program and the accompanying materials are made available under
# the terms of the under the Apache License, Version 2.0 (the "License”);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
