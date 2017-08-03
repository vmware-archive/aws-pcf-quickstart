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
import os
import re
import sys

import jinja2
import yaml

versioned_file_name = ""
ami_mapping_dir = "../ami-mapping"

for file_name in os.listdir(ami_mapping_dir):
    if re.match(r'ami-mapping-.*\.json', file_name):
        versioned_file_name = file_name

if versioned_file_name == "":
    print("Unable to find ami-mapping file")
    sys.exit(1)

with open(os.path.join(ami_mapping_dir, versioned_file_name)) as f:
    raw_mapping = json.load(f)
    mapping = {}
    for key in raw_mapping:
        mapping[key] = {"64": raw_mapping[key]}

mapping_yaml = yaml.dump(mapping, default_flow_style=False)

with open("templates/quickstart-template.j2.yml", 'r') as f:
    quickstart_template = jinja2.Template(f.read())

context = {
    "bootstrap_ami_mapping": mapping_yaml
}

with open("cloudformation/quickstart-template-rc.yml", 'w') as template_file:
    template_file.write(quickstart_template.render(context))
