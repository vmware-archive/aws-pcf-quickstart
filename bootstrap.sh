#!/usr/bin/env bash
set -ex

cd /home/ubuntu/quickstart

export PATH=./bin:$PATH
sudo pip3 install ./vendor/*

# todo: hard-coding version for the moment
export OPS_MANAGER_VERSION=1.10.4
export ERT_VERSION=1.10.4-build.1
export AWS_BROKER_VERSION=1.2.0.147
export TILE_BUCKET_S3_NAME=pcf-quickstart-tiles
export TILE_BUCKET_REGION=us-west-2

python3 quickstart.py configure-opsman-auth
python3 quickstart.py configure-opsman-director
python3 quickstart.py apply-changes
python3 quickstart.py download-tiles
python3 quickstart.py upload-assets '/tmp'
python3 quickstart.py configure-ert
python3 quickstart.py apply-changes
