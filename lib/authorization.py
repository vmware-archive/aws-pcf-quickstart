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

import re
import settings
import util
import functools
import requests


def header_value(auth_token: str):
    success = False
    if re.search("-r$", auth_token):
        print("Refresh Token")
        # then it's a refresh token
        access_token, success = util.exponential_backoff(
            functools.partial(
                refresh_token_grant,
                auth_token
            ),
            check_refresh_succeeded
        )

        if success:
            authHeaderValue = "Bearer {}".format(access_token)
    else:
        # it isn't a refresh token. It could be a legacy token... or just plain
        # wrong. Either way, hand back a legacy auth
        authHeaderValue = "Token {}".format(auth_token)
        print("Legacy Token")
        success = True

    print("Auth token success is {}".format(success))
    return authHeaderValue, success


def refresh_token_grant(refresh_token: str):
    response = requests.post(
        url='https://network.pivotal.io/api/v2/authentication/access_tokens',
        headers={
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
        json={"refresh_token": refresh_token},
    )
    print(response)
    if response.status_code < 300:
        try:
            access_token = response.json()["access_token"]

        except:
            print("Could not decode access token json")
            return None, False

    return access_token, response.status_code < 300


def check_refresh_succeeded(result):
    _, success = result
    return success
