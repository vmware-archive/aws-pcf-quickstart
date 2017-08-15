#!/usr/bin/env bash

docker build ci -t cfplatformeng/quickstart-ci
echo "Hard-coded to push tag 1"
docker tag cfplatformeng/quickstart-ci cfplatformeng/quickstart-ci:1
docker push cfplatformeng/quickstart-ci
