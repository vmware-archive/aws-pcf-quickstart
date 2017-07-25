# pivotal-cloud-foundry-quickstart
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

import socket
import time

import settings


def check_dns(domain: str):
    try:
        return socket.gethostbyname(domain)
    except socket.gaierror:
        return ""


def wait_for_dns(my_settings: settings.Settings):
    while True:
        domain = "opsman.{}".format(my_settings.pcf_input_domain)
        print("Checking DNS entry {}".format(domain))
        ip = check_dns(domain)
        if ip == my_settings.pcf_pcfopsmanagerinstanceip:
            return 0
        else:
            time.sleep(5)
