#! /usr/bin/env python3

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
    ert_metadata_file = find_file("ert-tile/metadata.json")
    broker_metadata_file = find_file("aws-broker-tile/metadata.json")

    with open('./ami-version/version', 'r') as version_file:
        ami_version = version_file.read()

    with open('./quickstart-repo/ci/packer.j2.json', 'r') as template_file:
        template = jinja2.Template(template_file.read())

        ctx = {
            "aws_access_key_id": os.environ['AWS_ACCESS_KEY_ID'],
            "aws_secret_access_key": os.environ['AWS_SECRET_ACCESS_KEY'],
            "ert_metadata_file": ert_metadata_file,
            "broker_metadata_file": broker_metadata_file,
            "ami_version": ami_version
        }

        rendered = template.render(ctx)
        with open('packer.json', 'w') as packer_file:
            packer_file.write(rendered)

    cmd = "packer build packer.json"

    sys.exit(subprocess.call(cmd, shell=True))


if __name__ == "__main__":
    main(sys.argv)
