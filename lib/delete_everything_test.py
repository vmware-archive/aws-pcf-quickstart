# pivotal-cloud-foundry-quickstart
#
# Copyright (c) 2017-Present Pivotal Software, Inc. All Rights Reserved.
#
# This program and the accompanying materials are made available under
# the terms of the under the Apache License, Version 2.0 (the "License”);
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

import unittest

import botocore.exceptions
from mock import Mock, patch

import delete_everything
from settings import Settings


class TestDeleteEverything(unittest.TestCase):
    def setUp(self):
        self.settings = Mock(Settings)
        self.settings.region = 'canada-1a'
        self.settings.pcf_elasticruntimes3buildpacksbucket = 'bucket-bp'
        self.settings.pcf_elasticruntimes3dropletsbucket = 'bucket-dp'
        self.settings.pcf_elasticruntimes3packagesbucket = 'bucket-pkg'
        self.settings.pcf_elasticruntimes3resourcesbucket = 'bucket-rsc'
        self.settings.pcf_iam_access_key_id = 'key-vale'
        self.settings.pcf_iam_secret_access_key = 'key-secret'
        self.settings.debug = False

    @patch('om_manager.is_opsman_configured')
    @patch('delete_everything.expire_bucket')
    @patch('util.exponential_backoff_cmd')
    @patch('om_manager.get_om_with_auth')
    def test_om_delete_installation(self, mock_auth, mock_backoff, mock_expire_bucket, mock_is_opsman_configured):
        mock_backoff.return_value =  "", "", 0
        mock_is_opsman_configured.return_value = True

        mock_auth.return_value = "om-with-auth-for-realz"

        delete_everything.delete_everything(self.settings)

        mock_backoff.assert_called_with(
            "om-with-auth-for-realz delete-installation", False
        )

    @patch('om_manager.is_opsman_configured')
    @patch('delete_everything.expire_bucket')
    @patch('util.exponential_backoff_cmd')
    @patch('om_manager.get_om_with_auth')
    def test_om_delete_installation_fails(self, mock_auth, mock_backoff, mock_expire_bucket, mock_is_opsman_configured):
        mock_backoff.return_value = "Fail", "",  1
        mock_is_opsman_configured.return_value = True

        result = delete_everything.delete_everything(self.settings)

        self.assertEqual(result[0], "Fail")
        self.assertEqual(result[2], 1)

    @patch('om_manager.is_opsman_configured')
    @patch('delete_everything.delete_bucket')
    @patch('delete_everything.expire_bucket')
    @patch('util.exponential_backoff_cmd')
    @patch('om_manager.get_om_with_auth')
    def test_expire_buckets(self, mock_auth, mock_backoff, mock_expire_bucket, mock_delete_bucket, mock_is_opsman_configured):
        mock_backoff.return_value = "", "", 0
        mock_is_opsman_configured.return_value = True

        return_code = delete_everything.delete_everything(self.settings)

        self.assertEqual(return_code, 0)
        self.assertEqual(mock_expire_bucket.call_count, 5)
        mock_expire_bucket.assert_called_with(
            self.settings, "bucket-rsc"
        )
        self.assertEqual(mock_delete_bucket.call_count, 0)

    @patch('om_manager.is_opsman_configured')
    @patch('delete_everything.delete_bucket')
    @patch('delete_everything.expire_bucket')
    @patch('util.exponential_backoff_cmd')
    @patch('om_manager.get_om_with_auth')
    def test_expire_buckets(self, mock_auth, mock_backoff, mock_expire_bucket, mock_delete_bucket, mock_is_opsman_configured):
        mock_backoff.return_value = "", "", 0
        mock_is_opsman_configured.return_value = True

        result = delete_everything.delete_everything(self.settings, True)

        self.assertEqual(result[2], 0)
        self.assertEqual(mock_delete_bucket.call_count, 5)
        mock_delete_bucket.assert_called_with(
            self.settings, "bucket-rsc"
        )
        self.assertEqual(mock_expire_bucket.call_count, 0)

    @patch('boto3.client')
    @patch('util.exponential_backoff_cmd')
    @patch('om_manager.get_om_with_auth')
    def test_delete_buckets(self, mock_auth, mock_backoff, mock_client_constructor):
        mock_client = Mock()
        mock_client.list_objects_v2.return_value = {}
        mock_client_constructor.return_value = mock_client

        delete_everything.delete_bucket(self.settings, "bucket-rsc")

        self.assertEqual(mock_client.delete_bucket.call_count, 1)
        mock_client.delete_bucket.assert_called_with(
            Bucket="bucket-rsc"
        )

    @patch('om_manager.is_opsman_configured')
    @patch('boto3.client')
    @patch('util.exponential_backoff_cmd')
    @patch('om_manager.get_om_with_auth')
    def test_delete_buckets_idempotent(self, mock_auth, mock_backoff, mock_client_constructor, mock_is_opsman_configured):
        mock_backoff.return_value = "", "", 0
        mock_is_opsman_configured.return_value = True

        mock_client = Mock()
        no_suck_bucket_error = botocore.exceptions.ClientError({'Error': {'Code': 'NoSuchBucket'}}, 'DeleteOrSomething')
        mock_client.list_objects_v2.side_effect = no_suck_bucket_error

        mock_client_constructor.return_value = mock_client

        delete_everything.delete_everything(self.settings, "bucket-rsc")

        self.assertEqual(mock_client.delete_bucket.call_count, 0)


    @patch('boto3.client')
    @patch('util.exponential_backoff_cmd')
    @patch('om_manager.get_om_with_auth')
    def test_expire_bucket(self, mock_auth, mock_backoff, mock_client_constructor):
        mock_client = Mock()
        mock_client_constructor.return_value = mock_client

        delete_everything.expire_bucket(self.settings, "bucket-rsc")

        self.assertEqual(mock_client.put_bucket_lifecycle_configuration.call_count, 1)

    @patch('om_manager.is_opsman_configured')
    @patch('util.exponential_backoff_cmd')
    @patch('om_manager.get_om_with_auth')
    def test_skips_delete_installation_when_opsman_not_configured(self, mock_auth, mock_exponential_backoff, mock_is_opsman_configured):
        mock_is_opsman_configured.return_value = False

        delete_everything.delete_everything(self.settings)

        mock_exponential_backoff.assert_not_called()
