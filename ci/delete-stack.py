# aws-pcf-quickstart
#
# Copyright (c) 2017-Present Pivotal Software, Inc. All Rights Reserved.
#
# This program and the accompanying materials are made available under
# the terms of the under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import sys
import time

import boto3
import os

aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']


def describe_stack_status(cloudformation_client, stack_id):
    describe_response = cloudformation_client.describe_stacks(StackName=stack_id)
    stack = describe_response.get("Stacks")[0]

    return stack.get('StackStatus')


with open('../aws-pcf-concourse-state/stackid', 'r') as file:
    stack_metadata = json.loads(file.read())
    stack_id = stack_metadata['stack_id']
    aws_region = stack_metadata['region']

cf_client = boto3.client(
    service_name='cloudformation', region_name=aws_region, aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

response = cf_client.describe_stacks(StackName=stack_id)
stacks = response.get('Stacks')
stack_name = stacks[0].get('StackName')

print("Deleting stack {}".format(stack_id))
cf_client.delete_stack(StackName=stack_id)

stack_status = describe_stack_status(cf_client, stack_id)
while stack_status == 'DELETE_IN_PROGRESS':
    time.sleep(60)
    stack_status = describe_stack_status(cf_client, stack_id)
    print("Checking status got {}".format(stack_status))

print("Final status {}".format(stack_status))
if stack_status != 'DELETE_COMPLETE':
    print("Stack deletion did not complete, exiting. Final status was {}".format(stack_status))
    sys.exit(1)
else:
    sys.exit(0)
