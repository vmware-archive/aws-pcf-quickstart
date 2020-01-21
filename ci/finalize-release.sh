#!/bin/bash -e

export IMAGE_VERSION=$(cat opsman-image/version)

cp quickstart-scripts-alpha/quickstart.tgz output/quickstart-`cat version/version`.tgz

spruce json templates/assets/deployment.yml \
    | jq -r '.tiles | map("- \(.name)/\(.version) (\(.stemcell.product_slug | split("-") | .[-1])/\(.stemcell.release_version))") | .[]' > notes.md
echo "- ops-manager/${IMAGE_VERSION}" >> notes.md
