# aws-pcf-quickstart
#
# Copyright (c) 2017-Present Pivotal Software, Inc. All Rights Reserved.
#
# This program and the accompanying materials are made available under
# the terms of the under the Apache License, Version 2.0 (the "License");
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

import enum
import functools
import json

import requests

import settings
import util

max_retries = 5


def check_eula_succeeded(returned):
    response, result = returned
    return result == EULAResult.SUCCESS


def accept_ert_eula(my_settings: settings.Settings):
    response, result = util.exponential_backoff(
        functools.partial(post_eula, my_settings, my_settings.ert_release_id),
        check_eula_succeeded
    )
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


