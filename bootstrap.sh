#!/usr/bin/env bash
set -ex

cd /home/ubuntu/quickstart

export PATH=./bin:$PATH
sudo pip3 install ./vendor/*

python3 quickstart.py configure-opsman-auth
python3 quickstart.py configure-opsman-director
python3 quickstart.py apply-changes
#python3 quickstart.py download-tiles
python3 quickstart.py upload-assets '/home/ubuntu/tiles'
python3 quickstart.py upload-stemcell
python3 quickstart.py configure-ert
python3 quickstart.py apply-changes
