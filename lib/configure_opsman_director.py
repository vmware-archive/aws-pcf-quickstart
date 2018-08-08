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

from jinja2 import Template
import boto3
import om_manager
import os
from os.path import expanduser
from settings import Settings
import util
import tempfile


def configure_opsman_director(my_settings: Settings):
    keyname, keybytes = generate_ssh_keypair(my_settings)

    template_ctx = {
        "zones": my_settings.zones,
        "access_key_id": my_settings.pcf_iamuseraccesskey,
        "secret_access_key": my_settings.pcf_iamusersecretaccesskey,
        "vpc_id": my_settings.pcf_vpc,
        "security_group": my_settings.pcf_vmssecuritygroupid,
        "key_pair_name": keyname,
        "ssh_private_key": keybytes.replace("\n", "\\n"),
        "region": my_settings.region,
        "encrypted": "false",
        "pcf_management_subnet_az1": my_settings.pcf_pcfmanagementsubnetaz1,
        "pcf_management_subnet_az2": my_settings.pcf_pcfmanagementsubnetaz2,
        "pcf_management_subnet_az3": my_settings.pcf_pcfmanagementsubnetaz3,
        "pcf_ert_subnet_az1": my_settings.pcf_pcfertsubnetaz1,
        "pcf_ert_subnet_az2": my_settings.pcf_pcfertsubnetaz2,
        "pcf_ert_subnet_az3": my_settings.pcf_pcfertsubnetaz3,
        "pcf_services_subnet_az1": my_settings.pcf_pcfservicessubnetaz1,
        "pcf_services_subnet_az2": my_settings.pcf_pcfservicessubnetaz2,
        "pcf_services_subnet_az3": my_settings.pcf_pcfservicessubnetaz3,
        "az1": my_settings.pcf_pcfavailabilityzone1,
        "az2": my_settings.pcf_pcfavailabilityzone2,
        "az3": my_settings.pcf_pcfavailabilityzone3,
        "singleton_availability_zone": my_settings.pcf_pcfavailabilityzone1
    }
    with open("templates/director_config.j2.yml", 'r') as f:
        director_template = Template(f.read())

    director_config = director_template.render(template_ctx)
    with tempfile.NamedTemporaryFile(mode='w') as f:
        f.write(director_config)

        cmd = om_manager.get_om_with_auth(my_settings) + [
            "configure-director",
            "--config", f.name
        ]
        out, err, exit_code = util.run_command(cmd)
        if out != "":
            print(out)
        if err != "":
            print(err)
        if exit_code != 0:
            return out, err, exit_code

    return out, err, 0


def generate_ssh_keypair(my_settings: Settings):
    client = boto3.client(service_name='ec2', region_name=my_settings.region)

    keyname = my_settings.get_pcf_keypair_name()
    response = client.create_key_pair(
        DryRun=False,
        KeyName=keyname
    )

    home = expanduser("~/.ssh")
    pem_file = '{}/{}.pem'.format(home, keyname)

    with open(pem_file, 'w') as keyfile:
        keyfile.write(response.get('KeyMaterial'))
    os.chmod(pem_file, 0o400)

    return keyname, response.get('KeyMaterial')
