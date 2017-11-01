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

import unittest

from mock import patch, Mock,  mock_open

import json
import settings

input_params = {
    'Stacks': [
        {
            'Parameters': [
                {
                    'ParameterValue': 'admin@example.com',
                    'ParameterKey': 'AdminEmail'
                },
                {
                    'ParameterValue': 'my-key',
                    'ParameterKey': 'PCFKeyPair'
                },
                {
                    'ParameterValue': 'elb-pre-yo',
                    'ParameterKey': 'ElbPrefix'
                },
                {
                    'ParameterValue': 'abc123',
                    'ParameterKey': 'PivnetToken'
                },
                {
                    'ParameterValue': 'my-zone-id',
                    'ParameterKey': 'HostedZoneId'
                },
                {
                    'ParameterValue': 'pcf.example.com',
                    'ParameterKey': 'Domain'
                }
            ]
        }
    ]
}

param_json_doc = """
{
  "PcfRdsPassword": "monkey123",
  "PcfRdsUsername": "admin",
  "PcfPrivateSubnetAvailabilityZone": "canada-1a",
  "PcfPrivateSubnet2AvailabilityZone": "canada-1b",
  "PcfOpsManagerAdminPassword": "monkey123",
  "PcfDeploymentSize": "Starter"
}
"""

params_store_output = {
    'InvalidParameters': [],
    'ResponseMetadata': {
        'RetryAttempts': 0,
        'HTTPHeaders': {
            'content-type': 'application/x-amz-json-1.1',
            'x-amzn-requestid': 'abcd-efg',
            'date': 'Wed, 03 May 2017 17:00:47 GMT',
            'content-length': '262'
        },
        'RequestId': '1234-5678',
        'HTTPStatusCode': 200
    },
    'Parameter': {
        "Name": "MyStack.SSMParameterJSON",
        "Type": "String",
        "Value": param_json_doc
    }
}


class TestSettings(unittest.TestCase):
    def setUp(self):
        self.meta_json = """
{
  "StackName": "pcf-stack",
  "StackId": "arn:aws:cloudformation:us-east-1:429148957415:stack/pcf-stack/1cb9cd21-2c4e-11e7-8e25-50fae98a10fe",
  "Region": "canada-west-1"
}
"""
        self.version_config_json = """
{
  "stemcell": {
    "releaseDate": "2017-04-26",
    "sha256": "ece6b9aaa4af20c180c446582bfa8e7d29681e2aac06c5d3d978a92c84432237",
    "version": "3363.20",
    "id": 5200
  },
  "ert": {
    "releaseDate": "2017-05-04",
    "sha256": "70070bf22231d9971c97b8deb8c4cd5ba990d24101e5398d0ccc70778060dbea",
    "version": "1.10.8",
    "id": 5334
  }
}
"""

        mock_client_contructor = Mock()

        with patch('boto3.client', mock_client_contructor):
            with patch('settings.read_meta') as mock_read_meta:
                mock_read_meta.return_value = json.loads(self.meta_json)
                with patch('settings.read_version_config') as mock_read_version_config:
                    mock_read_version_config.return_value = json.loads(self.version_config_json)

                    mock_client = Mock()
                    mock_client_contructor.return_value = mock_client
                    mock_client.describe_stacks.return_value = input_params
                    mock_client.get_parameter.return_value = params_store_output

                    self.settings = settings.Settings()

    def test_pcf_input(self):
        self.assertEqual(self.settings.pcf_input_pivnettoken, "abc123")
        self.assertEqual(self.settings.pcf_input_pcfkeypair, "my-key")
        self.assertEqual(self.settings.pcf_input_adminemail, "admin@example.com")
        self.assertEqual(self.settings.pcf_input_elbprefix, "elb-pre-yo")
        self.assertEqual(self.settings.pcf_input_hostedzoneid, "my-zone-id")
        self.assertEqual(self.settings.pcf_input_domain, "pcf.example.com")
        self.assertEqual(self.settings.pcf_opsmanageradminpassword, "monkey123")

    def test_parse_meta(self):
        self.assertEqual(self.settings.stack_name, "pcf-stack")
        self.assertEqual(
            self.settings.stack_id,
            "arn:aws:cloudformation:us-east-1:429148957415:stack/pcf-stack/1cb9cd21-2c4e-11e7-8e25-50fae98a10fe"
        )
        self.assertEqual(self.settings.region, "canada-west-1")

    def test_chunk_list(self):
        l = ['a', 'b', 'c', 'd', 'e']
        chunks = settings.chunk(l, 2)

        self.assertEqual(chunks[0], ['a', 'b'])
        self.assertEqual(chunks[1], ['c', 'd'])
        self.assertEqual(chunks[2], ['e'])

    def test_parses_paramaters(self):
        self.assertEqual(self.settings.pcf_rdsusername, "admin")
        self.assertEqual(self.settings.pcf_rdspassword, "monkey123")
        self.assertEqual(self.settings.pcf_privatesubnetavailabilityzone, "canada-1a")
        self.assertEqual(self.settings.pcf_privatesubnet2availabilityzone, "canada-1b")
        self.assertEqual(self.settings.pcf_pcfdeploymentsize, "Starter")

    def test_default_values(self):
        self.assertEqual(self.settings.opsman_user, 'admin')

    def test_get_s3_endpoint(self):
        self.assertEqual(self.settings.get_s3_endpoint(), "s3-canada-west-1.amazonaws.com")

    def test_get_s3_endpoint_east1(self):
        self.settings.region = "us-east-1"
        self.assertEqual(self.settings.get_s3_endpoint(), "s3.amazonaws.com")

    def test_parse_version_config(self):
        self.assertEqual(self.settings.ert_release_id, 5334)
        self.assertEqual(self.settings.ert_release_version, "1.10.8")
        self.assertEqual(
            self.settings.ert_release_sha256,
            "70070bf22231d9971c97b8deb8c4cd5ba990d24101e5398d0ccc70778060dbea"
        )

        self.assertEqual(self.settings.stemcell_release_version, "3363.20")
        self.assertEqual(
            self.settings.stemcell_release_sha256,
            "ece6b9aaa4af20c180c446582bfa8e7d29681e2aac06c5d3d978a92c84432237"
        )

    @patch('os.path.isfile')
    def test_resources_created(self, isfile_mock):
        isfile_mock.return_value = False
        self.assertFalse(self.settings.resources_created)

        isfile_mock.return_value = True
        self.assertTrue(self.settings.resources_created)

    def test_toggle_resources_created(self):
        my_mock_open = mock_open()
        with patch('settings.open', my_mock_open):
            self.settings.toggle_resources_created()
        my_mock_open.assert_called()