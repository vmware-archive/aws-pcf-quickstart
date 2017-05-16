#!/usr/bin/python

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
        sys.exit(p.returncode)

    settings = json.loads(out)

    for setting in settings['installations']:
        status = [a for a in setting['additions'] if a['identifier'] == identifier]
        if len(status) > 0:
            return setting['status']

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
        else:
            print("p-bosh install in running")
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
        else:
            print("cf install in running")
            time.sleep(300)

    print("Done")

if __name__ == "__main__":
    main(sys.argv)
