#!/usr/bin/python
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
import subprocess
import sys
import time
import os


def check_status(password, opsman, identifier):
    cmd = "om -k -u admin -p {0} -t {1} curl -p /api/v0/installations".format(
        password, opsman
    )

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out_bytes, err_bytes = p.communicate()
    out = out_bytes.decode("utf-8").strip()

    if p.returncode != 0:
        print("curling opsman status failed")
        sys.exit(p.returncode)

    installations = json.loads(out)

    for installation in installations['installations']:
        status = [a for a in installation['additions'] if a['identifier'] == identifier]
        if len(status) > 0:
            return installation['status']

    return None


def main(argv):
    opsman = "https://opsman.{}".format(os.environ['AWS_CF_DOMAIN'])
    password = os.environ['AWS_CF_PASSWORD']

    status = None
    while (status == "running") or not status:
        status = check_status(password, opsman, "p-bosh")
        if status == "failed":
            print("p-bosh install failed")
            sys.exit(1)
        elif status == "succeeded":
            print("p-bosh install succeeded")
            break
        elif status is None:
            print("p-bosh install doesn't exist yet")
            time.sleep(30)
        else:
            print("p-bosh install is running")
            time.sleep(300)

    status = None
    while (status == "running") or not status:
        status = check_status(password, opsman, "cf")
        if status == "failed":
            print("cf install failed")
            sys.exit(1)
        elif status == "succeeded":
            print("cf install succeeded")
            break
        elif status is None:
            print("cf install doesn't exist yet")
            time.sleep(30)
        else:
            print("cf install is running")
            time.sleep(300)

    print("Done")

if __name__ == "__main__":
    main(sys.argv)
