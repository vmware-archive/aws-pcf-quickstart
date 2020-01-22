#!/bin/bash

set -e
set -x

export IMAGE_VERSION=$(cat opsman-tile/version)

cp quickstart-scripts-alpha/quickstart.tgz output/quickstart-`cat version/version`.tgz

spruce json quickstart-repo/templates/assets/deployment.yml \
    | jq -r '.tiles | map("- \(.name)/\(.version) (\(.stemcell.product_slug | split("-") | .[-1])/\(.stemcell.release_version))") | .[]' > output/notes.md
echo "- ops-manager/${IMAGE_VERSION}" >> output/notes.md
