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
from subprocess import call

from jinja2 import Template

import om_manager
import util
import random
import string
from settings import Settings


def configure_aws_service_broker(my_settings: Settings):
    out, err, exit_code = om_manager.stage_product("aws-service-broker", my_settings)
    if exit_code != 0:
        print("Failed to stage aws-service-broker")
        return out, err, exit_code

    out, err, exit_code = configure_tile_az(my_settings, 'aws-service-broker')
    if exit_code != 0:
        print("Failed to configure az aws-service-broker")
        return out, err, exit_code

    out, err, exit_code = configure_aws_service_broker_config(my_settings)
    if exit_code != 0:
        print("Failed to configure aws-service-broker")
        return out, err, exit_code

    return "", "", 0


def configure_aws_service_broker_config(my_settings: Settings):
    cert, key = generate_ssl_cert(my_settings)
    aws_config_template_ctx = {
        "aws_region": my_settings.region,
        "aws_service_bucket": my_settings.pcf_elasticruntimes3buildpacksbucket,
        "aws_s3_region": my_settings.region,
        "aws_iam_access_key_id": my_settings.broker_iamuseraccesskey,
        "aws_iam_secret_access_key": my_settings.broker_iamusersecretaccesskey,
        "pcf_skipsslvalidation": my_settings.pcf_input_skipsslvalidation,
        "cert": cert.replace("\n", "\\n"),
        "key": key.replace("\n", "\\n")
    }
    with open("templates/aws_service_broker_config.j2.json", 'r') as f:
        aws_broker_template = Template(f.read())
    aws_config = om_manager.format_om_json_str(
        aws_broker_template.render(aws_config_template_ctx))
    cmd = om_manager.get_om_with_auth(my_settings) + [
        "configure-product",
        "-n", "aws-service-broker",
        "-p", aws_config]
    return util.exponential_backoff_cmd(cmd)


def configure_tile_az(my_settings: Settings, tile_name: str):
    az_template_ctx = {
        "singleton_availability_zone": my_settings.zones[0],
        "zones": my_settings.zones
    }
    with open("templates/tile_az_service_config.j2.json", 'r') as f:
        az_template = Template(f.read())
    az_config = om_manager.format_om_json_str(
        az_template.render(az_template_ctx))
    cmd = om_manager.get_om_with_auth(my_settings) + [
        "configure-product",
        "-n", tile_name,
        "-pn", az_config]

    return util.exponential_backoff_cmd(cmd)


def generate_ssl_cert(my_settings: Settings):
    call("scripts/gen_ssl_certs.sh {}".format(my_settings.pcf_input_domain), shell=True)
    with open("{}.crt".format(my_settings.pcf_input_domain), 'r') as cert_file:
        cert = cert_file.read()

    with open("{}.key".format(my_settings.pcf_input_domain), 'r') as key_file:
        key = key_file.read()

    return cert, key
