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
import authorization

max_retries = 5


def check_eula_succeeded(returned):
    response, result = returned
    return result == EULAResult.SUCCESS


def accept_eulas(my_settings: settings.Settings):
    out, err, exit_code = accept_ert_eula(my_settings)
    if exit_code != 0:
        return out, err, exit_code
    return accept_stemcell_eula(my_settings)


def accept_ert_eula(my_settings: settings.Settings):
    response, result = util.exponential_backoff(
        functools.partial(post_eula, my_settings,
                          "elastic-runtime", my_settings.ert_release_id),
        check_eula_succeeded
    )
    if result == EULAResult.SUCCESS:
        return "Success", "", 0
    else:
        return "Failed to accept ERT EULA; status code from Pivotal Network {}".format(response.status_code), "", 1


def accept_stemcell_eula(my_settings: settings.Settings):
    response, result = util.exponential_backoff(
        functools.partial(post_eula, my_settings, "stemcells",
                          my_settings.stemcell_release_id),
        check_eula_succeeded
    )
    if result == EULAResult.SUCCESS:
        return "Success", "", 0
    else:
        return "Failed to accept stemcell EULA; status code from Pivotal Network {}".format(response.status_code), "", 1


class EULAResult(enum.Enum):
    SUCCESS = 0,
    FAILURE = 1,
    RETRY = 2


def post_eula(my_settings: settings.Settings, slug: str, release_id: int):
    auth_header, success = authorization.header_value(my_settings)
    if not success:
        return None, EULAResult.FAILURE

    response = requests.post(
        url='https://network.pivotal.io/api/v2/products/{}/releases/{}/eula_acceptance'.format(
            slug, release_id),
        headers={
            'Authorization': auth_header,
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
