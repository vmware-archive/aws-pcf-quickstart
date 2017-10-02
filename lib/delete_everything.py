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

import boto3

import om_manager
import util
from settings import Settings


def delete_everything(my_settings: Settings):
    if om_manager.is_opsman_configured(my_settings):
        my_settings.pcf_input_skipsslvalidation = "true"
        cmd = "{om_with_auth} delete-installation".format(
            om_with_auth=om_manager.get_om_with_auth(my_settings)
        )
        # delete blocks on apply-changes, but if other apply changes in progress, doesn't queue up its own
        util.exponential_backoff_cmd(cmd)
        out, err, return_code = util.exponential_backoff_cmd(cmd)
        if return_code != 0:
            print("OM cmd failed to delete installation {}".format(return_code))
            return out, err, return_code

    buckets = [
        my_settings.pcf_opsmanagers3bucket,
        my_settings.pcf_elasticruntimes3buildpacksbucket,
        my_settings.pcf_elasticruntimes3dropletsbucket,
        my_settings.pcf_elasticruntimes3packagesbucket,
        my_settings.pcf_elasticruntimes3resourcesbucket
    ]

    # todo: should we delete the keypair...?

    for bucket_name in buckets:
        try:
            expire_bucket(my_settings, bucket_name)
        except Exception as e:
            print(e)
    return "", "", 0


def expire_bucket(my_settings: Settings, bucket_name: str):
    s3 = boto3.client(
        service_name='s3', region_name=my_settings.region,
        aws_access_key_id=my_settings.pcf_iamuseraccesskey,
        aws_secret_access_key=my_settings.pcf_iamusersecretaccesskey
    )
    s3.put_bucket_lifecycle_configuration(
        Bucket=bucket_name,
        LifecycleConfiguration={
            'Rules': [
                {
                    'Expiration': {
                        'Date': '2000-01-01'
                    },
                    'Prefix': "",
                    'Status': 'Enabled'
                }
            ]
        }
    )
