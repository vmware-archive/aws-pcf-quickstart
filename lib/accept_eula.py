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

def accept_eulas(my_settings: settings.Settings):
    out, err, exit_code = accept_ert_eula(my_settings)
    if exit_code != 0:
        return out, err, exit_code
    out, err, exit_code = accept_stemcell_eula(my_settings)
    if exit_code != 0:
        return out, err, exit_code
    return out, "", 0

def accept_ert_eula(my_settings: settings.Settings):
    out, err, exit_code = post_eula(my_settings, "elastic-runtime", my_settings.ert_release_id)

    if exit_code != 0:
        return "Failed to accept ERT EULA; got message from Pivotal Network: {}".format(out), err, exit_code
    return "Success; {}".format(out), "", 0

def accept_stemcell_eula(my_settings: settings.Settings):
    out, err, exit_code = post_eula(my_settings, "stemcells", my_settings.stemcell_release_id)

    if exit_code != 0:
        return "Failed to accept stemcell EULA; got message from Pivotal Network: {}".format(out), err, exit_code
    return "Success; {}".format(out), "", 0

def post_eula(my_settings: settings.Settings, slug: str, release_id: int):
    cmd = "pivnet login --api-token={token}".format(token=my_settings.pcf_input_pivnettoken)
    out, err, exit_code = util.exponential_backoff_cmd(cmd)

    if exit_code != 0:
        return out, err, exit_code

    cmd = "pivnet curl -X POST /products/{}/releases/{}/eula_acceptance".format(slug, release_id)
    out, err, exit_code = util.exponential_backoff_cmd(cmd)
    out_json = json.loads(out)

    if exit_code != 0:
        return out_json["message"], err, exit_code
    if exit_code == 0:
        return "accepted: {} at: {}".format(out_json["_links"]["eula"]["href"], out_json["accepted_at"]), err, exit_code
