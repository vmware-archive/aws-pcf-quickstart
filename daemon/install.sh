#!/usr/bin/env bash

set -x

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cp ${script_dir}/quickstart.service /lib/systemd/system/quickstart.service

systemctl reenable quickstart.service
systemctl restart quickstart.service
