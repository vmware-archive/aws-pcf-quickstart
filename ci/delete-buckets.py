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

import sys

import boto3
import botocore
import botocore.exceptions
import os


def delete_bucket(bucket_name: str, region: str, key: str, secret: str):
    print("Deleting bucket {}".format(bucket_name))
    s3_client = boto3.client(
        service_name='s3',
        region_name=region,
        aws_access_key_id=key,
        aws_secret_access_key=secret
    )
    try:
        while contents is not None:
            contents = s3_client.list_object_versions(
                Bucket=bucket_name).get('Contents')
            if contents is None:
                break
            s3_client.delete_objects(Bucket=bucket_name, Delete={
                'Objects': contents
            })

        s3_client.delete_bucket(Bucket=bucket_name)
    except botocore.exceptions.ClientError as e:
        error = e.response.get('Error')
        if not error or error.get('Code') != 'NoSuchBucket':
            raise e


def main():
    aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
    aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
    prefix = "pcf-int-"

    s3_client = boto3.client(
        service_name='s3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )
    response = s3_client.list_buckets()
    buckets = response.get('Buckets')
    if len(buckets) < 0:
        print("No buckets in response")
        print(response)
        sys.exit(0)

    print("Buckets: {}".format(buckets))
    for bucket in buckets:
        bucket_name = bucket.get('Name')
        response = s3_client.get_bucket_location(Bucket=bucket_name)
        bucket_region = response.get('LocationConstraint')
        if bucket_name.startswith(prefix):
            delete_bucket(bucket_name, bucket_region,
                          aws_access_key_id, aws_secret_access_key)


if __name__ == "__main__":
    main()
