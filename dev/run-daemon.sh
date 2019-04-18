#!/bin/bash

region=$(aws configure get region)
aws cloudformation list-stacks \
    --stack-status-filter CREATE_IN_PROGRESS CREATE_FAILED CREATE_COMPLETE \
    | jq --arg r $region '.StackSummaries |
      map(select(.StackName | contains("PCFBase") | not))[0] |
      {StackName: .StackName, StackId: .StackId, Region: $r}
    ' > /tmp/stack-meta.json

go run main.go daemon \
   --cache-dir=/tmp/cache \
   --metadata-file=/tmp/stack-meta.json
