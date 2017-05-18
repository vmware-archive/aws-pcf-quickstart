#! /usr/bin/env python3

import glob
import os
import subprocess
import sys

import jinja2


def main(argv):
    ert_file_match = glob.glob("ert-tile/*.pivotal")
    if len(ert_file_match) != 1:
        raise ValueError("Didn't correctly find ert pivotal file")
    ert_file = ert_file_match[0]

    with open('./ami-version/ami_version', 'r') as version_file:
        ami_version = version_file.read()

    with open('./quickstart-repo/ci/packer.j2.json', 'r') as template_file:
        template = jinja2.Template(template_file.read())

        ctx = {
            "aws_access_key_id": os.environ['AWS_ACCESS_KEY_ID'],
            "aws_secret_access_key": os.environ['AWS_SECRET_ACCESS_KEY'],
            "ert_file": ert_file,
            "ami_version": ami_version
        }

        rendered = template.render(ctx)
        with open('packer.json', 'w') as packer_file:
            packer_file.write(rendered)

    cmd = "packer build packer.json"

    subprocess.call(cmd, shell=True)


if __name__ == "__main__":
    main(sys.argv)
