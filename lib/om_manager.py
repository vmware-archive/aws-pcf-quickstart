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

import json
from subprocess import Popen, PIPE

import requests

import settings
import util

max_retries = 5


def format_om_json_str(om_json: str):
    return json.dumps(json.loads(om_json))


def config_opsman_auth(my_settings: settings.Settings):
    cmd = ["om",
           "-k",
           "--target", my_settings.opsman_url,
           "configure-authentication",
           "--username", my_settings.opsman_user,
           "--password", my_settings.pcf_opsmanageradminpassword,
           "--decryption-passphrase", my_settings.pcf_opsmanageradminpassword]
    return util.exponential_backoff_cmd(cmd)


def is_opsman_configured(my_settings: settings.Settings):
    url = my_settings.opsman_url + "/api/v0/installations"
    response = requests.get(url=url, verify=False)
    # if auth isn't configured yet, authenticated api endpoints give 400 rather than 401
    if response.status_code == 400:
        return False
    return True


def apply_changes(my_settings: settings.Settings):
    cmd = get_om_with_auth(my_settings) + ["apply-changes"]
    return util.exponential_backoff_cmd(cmd)


def curl_get(my_settings: settings.Settings, path: str):
    cmd = get_om_with_auth(my_settings) + ["curl",
                                           "--path", path]
    return util.run_command(cmd)


def curl_payload(my_settings: settings.Settings, path: str, data: str, method: str):
    cmd = get_om_with_auth(my_settings) + ["curl",
                                           "--path", path,
                                           "--request", method,
                                           "--data", data]
    return util.run_command(cmd)


def stage_product(product_name: str, my_settings: settings.Settings):
    # cmd = "{om_with_auth} curl --path /api/v0/available_products".format(
    #    om_with_auth=get_om_with_auth(my_settings)
    # )
    cmd = get_om_with_auth(my_settings) + ["curl",
                                           "--path", "/api/v0/available_products"]
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        print("Failed to query api")
        return out, err, p.returncode

    products = json.loads(out.decode())
    cf_version = [x['product_version']
                  for x in products if x['name'] == product_name][0]

    # ok to call multiple times, no-op when already staged
    cmd = get_om_with_auth(my_settings) + ["stage-product",
                                           "-p", product_name,
                                           "-v", cf_version]
    return util.exponential_backoff_cmd(cmd)


def get_om_with_auth(my_settings: settings.Settings):
    return ["om",
            "-k",
            "--target", my_settings.opsman_url,
            "--username", my_settings.opsman_user,
            "--password", my_settings.pcf_opsmanageradminpassword]
