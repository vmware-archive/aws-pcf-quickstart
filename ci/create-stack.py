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

import datetime
import json
import sys
import time

import boto3
import botocore.exceptions
import os
import random
import yaml


def select_random_region():
    with open("./templates/supported_regions.yml") as f:
        region_list = yaml.load(f).get('supported_regions')
        region_list.remove("us-west-1")  # our prod-ish stuff is in west-1, don't use that

    secure_random = random.SystemRandom()
    region = secure_random.choice(region_list)

    print("Stack will be created in {} to run integration".format(region))
    return region


def describe_stack_status(cloudformation_client, stack_id):
    describe_response = cloudformation_client.describe_stacks(StackName=stack_id)
    stack = describe_response.get("Stacks")[0]

    return stack.get('StackStatus')


def create_stack(template_path: str, aws_region: str):
    password = os.environ['AWS_CF_PASSWORD']
    domain = os.environ['AWS_CF_DOMAIN']
    hostedzoneid = os.environ['AWS_CF_HOSTEDZONEID']
    pcfkeypair = os.environ['AWS_CF_PCFKEYPAIR']
    pivnettoken = os.environ['AWS_CF_PIVNETTOKEN']
    aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
    aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']

    sslcertificatearn = os.environ[aws_region.upper().replace('-', '_') + '_SSLCERTIFICATEARN']

    parameters = [
        {"ParameterKey": "RdsPassword", "ParameterValue": password},
        {"ParameterKey": "HostedZoneId", "ParameterValue": hostedzoneid},
        {"ParameterKey": "SSLCertificateARN", "ParameterValue": sslcertificatearn},
        {"ParameterKey": "OpsManagerAdminPassword", "ParameterValue": password},
        {"ParameterKey": "Domain", "ParameterValue": domain},
        {"ParameterKey": "OpsManagerIngress", "ParameterValue": "0.0.0.0/0"},
        {"ParameterKey": "ElbPrefix", "ParameterValue": "my-pcf-elb"},
        {"ParameterKey": "PCFKeyPair", "ParameterValue": pcfkeypair},
        {"ParameterKey": "RdsUsername", "ParameterValue": "admin"},
        {"ParameterKey": "DeploymentSize", "ParameterValue": "Starter"},
        {"ParameterKey": "AdminEmail", "ParameterValue": "noreply@pivotal.io"},
        {"ParameterKey": "PivnetToken", "ParameterValue": pivnettoken},
        {"ParameterKey": "SkipSSLValidation", "ParameterValue": "true"},
        {"ParameterKey": "AcceptEULA", "ParameterValue": "Yes"},
        {"ParameterKey": "ForwardLogOutput", "ParameterValue": "true"},
        {"ParameterKey": "QSS3BucketName", "ParameterValue": "aws-pcf-quickstart-templates"}
    ]

    client = boto3.client(
        service_name='cloudformation', region_name=aws_region, aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

    with open(template_path, 'r') as template_file:
        template = template_file.read()

        stack_name = "pcf-int-{}".format(int(datetime.datetime.now().timestamp()))
        create_response = client.create_stack(
            StackName=stack_name,
            TemplateBody=template,
            Parameters=parameters,
            Capabilities=[
                'CAPABILITY_IAM',
            ],
        )
        stack_id = create_response.get("StackId")
        print("Created stack: {}".format(stack_id))
        stack_metadata = {
            "stack_id": stack_id,
            "region": aws_region,
            "ssl_cert_arn": sslcertificatearn
        }

        with open('stackid', 'w') as file:
            json.dump(stack_metadata, file)

        stack_status = describe_stack_status(client, stack_id)
        while stack_status == 'CREATE_IN_PROGRESS':
            time.sleep(60)
            try:
                stack_status = describe_stack_status(client, stack_id)
                print("Checking status got {}".format(stack_status))
            except botocore.exceptions.EndpointConnectionError as e:
                print("Hopefully AWS endpoint is coming back!", e)

        print("Final status {}".format(stack_status))
        if stack_status != "CREATE_COMPLETE":
            print("Stack creation did not complete, exiting...")
            sys.exit(1)
        else:
            sys.exit(0)


if __name__ == "__main__":
    template_path = sys.argv[1]
    if len(sys.argv) > 2:
        aws_region = sys.argv[2]
    else:
        aws_region = select_random_region()
    create_stack(template_path, aws_region)
