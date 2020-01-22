#!/bin/bash

set -e
set -x

export GITHUB_USER=${GITHUB_USER}
export GITHUB_PASSWORD=${GITHUB_PASSWORD}

version=$(cat version/version)


pushd aws-quickstart-repo

hub pull-request --base aws-quickstart/quickstart-pivotal-cloudfoundry:master --head cf-platform-eng/quickstart-pivotal-cloudfoundry:develop -m "Automated Pull Request from the starkandwayne CI - version ${version}" -m "view release notes here https://github.com/cf-platform-eng/aws-pcf-quickstart/releases/tag/${version}"

popd
