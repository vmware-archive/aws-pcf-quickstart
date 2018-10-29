#!/bin/bash

for region in $(aws ec2 describe-regions | jq -r '.Regions[] | .RegionName'); do
    echo "Region: ${region}"
    aws --region=${region} cloudformation describe-stacks | \
        jq '.Stacks[] | "\(.StackName): \(.StackStatus)"'
done
