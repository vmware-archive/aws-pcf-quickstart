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
from settings import Settings


def configure_ert(my_settings: Settings):
    out, err, exit_code = om_manager.stage_product("cf", my_settings)
    if exit_code != 0:
        print("Failed to stage ERT")
        return out, err, exit_code

    out, err, exit_code = configure_tile_az(my_settings, 'cf')
    if exit_code != 0:
        print("Failed to configure az ERT")
        return out, err, exit_code

    out, err, exit_code = configure_ert_config(my_settings)
    if exit_code != 0:
        print("Failed to configure ERT")
        return out, err, exit_code

    out, err, exit_code = modify_vm_types(my_settings)
    if exit_code != 0:
        print("Failed to modify VM types for ERT")
        return out, err, exit_code

    out, err, exit_code = configure_ert_resources(my_settings)
    if exit_code != 0:
        print("Failed to configure ERT")
        return out, err, exit_code

    out, err, exit_code = configure_ert_multiaz_resources(my_settings)
    if exit_code != 0:
        print("Failed to configure Multi AZ ERT")
        return out, err, exit_code

    return create_required_databases(my_settings)


def configure_ert_resources(my_settings: Settings):
    prefix = my_settings.stack_name
    if my_settings.pcf_input_elbprefix != "":
        prefix = my_settings.pcf_input_elbprefix
    ert_resource_ctx = {
        "router_lb_name": "{prefix}".format(prefix=prefix)
    }
    with open("templates/ert_resources_config.j2.json", 'r') as f:
        ert_resource_template = Template(f.read())
    ert_resource_config = om_manager.format_om_json_str(ert_resource_template.render(ert_resource_ctx))
    cmd = "{om_with_auth} configure-product -n cf -pr '{ert_resources}'".format(
        om_with_auth=om_manager.get_om_with_auth(my_settings),
        ert_resources=ert_resource_config
    )
    return util.exponential_backoff_cmd(cmd)


def configure_ert_multiaz_resources(my_settings: Settings):
    if my_settings.pcf_pcfnumberofazs > 1:
        with open("templates/ert_multiaz_resources_config.j2.json", 'r') as f:
            template = f.read()
    else:
        with open("templates/ert_singleaz_resources_config.j2.json", 'r') as f:
            template = f.read()

    ert_resource_config = om_manager.format_om_json_str(template)
    cmd = "{om_with_auth} configure-product -n cf -pr '{ert_resources}'".format(
        om_with_auth=om_manager.get_om_with_auth(my_settings),
        ert_resources=ert_resource_config
    )
    return util.exponential_backoff_cmd(cmd)


def configure_ert_config(my_settings: Settings):
    cert, key = generate_ssl_cert(my_settings)
    ert_config_template_ctx = {
        "pcf_rds_address": my_settings.pcf_rdsaddress,
        "pcf_rds_username": my_settings.pcf_rdsusername,
        "dns_suffix": my_settings.pcf_input_domain,
        "pcf_rds_password": my_settings.pcf_rdspassword,
        "admin_email": my_settings.pcf_input_adminemail,
        "pcf_elastic_runtime_s3_buildpacks_bucket": my_settings.pcf_elasticruntimes3buildpacksbucket,
        "pcf_elastic_runtime_s3_droplets_bucket": my_settings.pcf_elasticruntimes3dropletsbucket,
        "pcf_elastic_runtime_s3_packages_bucket": my_settings.pcf_elasticruntimes3packagesbucket,
        "pcf_elastic_runtime_s3_resources_bucket": my_settings.pcf_elasticruntimes3resourcesbucket,
        "pcf_iam_access_key_id": my_settings.pcf_iamuseraccesskey,
        "pcf_iam_secret_access_key": my_settings.pcf_iamusersecretaccesskey,
        "s3_endpoint": my_settings.get_s3_endpoint(),
        "s3_region": my_settings.region,
        "cert": cert.replace("\n", "\\n"),
        "key": key.replace("\n", "\\n")
    }
    with open("templates/ert_config.j2.json", 'r') as f:
        ert_template = Template(f.read())
    ert_config = om_manager.format_om_json_str(ert_template.render(ert_config_template_ctx))
    cmd = "{om_with_auth} configure-product -n cf -p '{ert_config}'".format(
        om_with_auth=om_manager.get_om_with_auth(my_settings),
        ert_config=ert_config
    )
    return util.exponential_backoff_cmd(cmd)


def configure_tile_az(my_settings: Settings, tile_name: str):
    az_template_ctx = {
        "singleton_availability_zone": my_settings.zones[0],
        "zones": my_settings.zones
    }
    with open("templates/tile_az_config.j2.json", 'r') as f:
        az_template = Template(f.read())
    az_config = om_manager.format_om_json_str(az_template.render(az_template_ctx))
    cmd = "{om_with_auth} configure-product -n {tile_name} -pn '{az_config}'".format(
        om_with_auth=om_manager.get_om_with_auth(my_settings),
        tile_name=tile_name,
        az_config=az_config
    )

    return util.exponential_backoff_cmd(cmd)


def create_required_databases(my_settings: Settings):
    cmd = "mysql -h {hostname} --user={username} --port={port} --password={password} < templates/required_dbs.sql".format(
        hostname=my_settings.pcf_rdsaddress,
        username=my_settings.pcf_rdsusername,
        port=my_settings.pcf_rdsport,
        password=my_settings.pcf_rdspassword
    )

    return util.exponential_backoff_cmd(cmd)


def modify_vm_types(my_settings: Settings):
    path = '/api/v0/vm_types'
    out, err, return_code = om_manager.curl_get(my_settings, path)
    if return_code != 0:
        if out != "":
            print(out)
        if err != "":
            print(err)
        return out, err, return_code

    response_json = json.loads(out)
    m4_exists = False

    for vm_type in response_json["vm_types"]:
        if vm_type["name"].startswith("m3"):
            response_json["vm_types"].remove(vm_type)
        elif vm_type["name"].startswith("m4"):
            m4_exists = True

    if not m4_exists:
        with open("templates/ert_vm_types.json") as template:
            additional_types = json.load(template)
            for a in additional_types:
                response_json["vm_types"].append(a)

    out, err, return_code = om_manager.curl_payload(my_settings, path, json.dumps(response_json), 'PUT')
    if return_code != 0:
        if out != "":
            print(out)
        if err != "":
            print(err)

    return out, err, return_code


def generate_ssl_cert(my_settings: Settings):
    call("scripts/gen_ssl_certs.sh {}".format(my_settings.pcf_input_domain), shell=True)
    with open("{}.crt".format(my_settings.pcf_input_domain), 'r') as cert_file:
        cert = cert_file.read()

    with open("{}.key".format(my_settings.pcf_input_domain), 'r') as key_file:
        key = key_file.read()

    return cert, key
