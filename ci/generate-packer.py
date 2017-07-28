#! /usr/bin/env python3
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


import glob
import os
import subprocess
import sys

import jinja2


def find_file(pattern):
    file_match = glob.glob(pattern)
    if len(file_match) != 1:
        raise ValueError("Didn't correctly find {} pivotal file".format(pattern))
    return file_match[0]


def main(argv):
    with open('./ami-version/version', 'r') as version_file:
        ami_version = version_file.read()

    with open('./quickstart-repo/ci/packer.j2.json', 'r') as template_file:
        template = jinja2.Template(template_file.read())

        ctx = {
            "aws_access_key_id": os.environ['AWS_ACCESS_KEY_ID'],
            "aws_secret_access_key": os.environ['AWS_SECRET_ACCESS_KEY'],
            "ami_version": ami_version
        }

        rendered = template.render(ctx)
        with open('packer.json', 'w') as packer_file:
            packer_file.write(rendered)

    cmd = "packer build packer.json"

    sys.exit(subprocess.call(cmd, shell=True))


if __name__ == "__main__":
    main(sys.argv)
