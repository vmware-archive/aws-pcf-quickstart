#!/usr/bin/env bash
set -ex

cd /home/ubuntu/quickstart

export PATH=./bin:$PATH
# sudo pip3 install ./vendor/*

# python3 -u quickstart.py

export GO111MODULE=on # manually active module mode
export GOFLAGS=-mod=vendor
go build .
./aws-pcf-quickstart build
