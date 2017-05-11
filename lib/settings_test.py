import os
import unittest

from mock import patch, mock_open, Mock

import settings

input_params = {
    'Stacks': [
        {
            'Parameters': [
                {
                    'ParameterValue': 'admin@example.com',
                    'ParameterKey': '13AdminEmail'
                },
                {
                    'ParameterValue': 'my-key',
                    'ParameterKey': '14PCFKeyPair'
                },
                {
                    'ParameterValue': 'elb-pre-yo',
                    'ParameterKey': '10ElbPrefix'
                },
                {
                    'ParameterValue': 'abc123',
                    'ParameterKey': '12PivnetToken'
                },
                {
                    'ParameterValue': 'my-zone-id',
                    'ParameterKey': '14HostedZoneId'
                },
                {
                    'ParameterValue': 'pcf.example.com',
                    'ParameterKey': '15Domain'
                }
            ]
        }
    ]
}
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
    'Parameters': [
        {
            'Type': 'String',
            'Value': 'monkey123',
            'Name': 'PcfRdsPassword'
        },
        {
            'Type': 'String',
            'Value': 'admin',
            'Name': 'PcfRdsUsername'
        },
        {
            'Type': 'String',
            'Value': 'canada-1a',
            'Name': 'PcfPrivateSubnetAvailabilityZone'
        },
        {
            'Type': 'String',
            'Value': 'canada-1b',
            'Name': 'PcfPrivateSubnet2AvailabilityZone'
        },
        {
            'Type': 'String',
            'Value': 'monkey123',
            'Name': 'PcfOpsManagerAdminPassword'
        },
        {
            'Type': 'String',
            'Value': '-----BEGIN RSA PRIVATE KEY-----foobarabc/q-----END RSA PRIVATE KEY-----',
            'Name': 'PcfPrivateSSHKey'
        }
    ]
}


class TestSettings(unittest.TestCase):
    def setUp(self):
        os.environ['DNS_SUFFIX'] = 'example.com'
        os.environ['OPS_MANAGER_VERSION'] = '99.0.1'
        os.environ['OPS_MANAGER_URL'] = 'https://some-random-ec2-domain.example.com'
        os.environ['OPS_MANAGER_ADMIN_PASSWORD'] = 'monkey123'
        os.environ["SSH_PRIVATE_KEY"] = "my-key-value-asdf-1234"
        os.environ["ERT_VERSION"] = "1.2.3"
        os.environ["AWS_BROKER_VERSION"] = "4.5.6"
        os.environ["TILE_BUCKET_S3_NAME"] = "my-bucket"
        os.environ["TILE_BUCKET_S3_ACCESS_KEY"] = "my-access-key"
        os.environ["TILE_BUCKET_S3_SECRET_ACCESS_KEY"] = "my-access-secret"
        os.environ["TILE_BUCKET_REGION"] = "canada-1"

        self.meta_json = """
{
  "StackName": "pcf-stack",
  "StackId": "arn:aws:cloudformation:us-east-1:429148957415:stack/pcf-stack/1cb9cd21-2c4e-11e7-8e25-50fae98a10fe",
  "Region": "canada-west-1"
}
"""

        my_mock_open = mock_open(read_data=self.meta_json)
        mock_client_contructor = Mock()
        settings.Settings.paramater_store_keys = [
            "PcfPrivateSubnetAvailabilityZone",
            "PcfPrivateSubnet2AvailabilityZone",
            "PcfRdsUsername",
            "PcfRdsPassword",
        ]

        with patch('boto3.client', mock_client_contructor):
            with patch('settings.open', my_mock_open):
                mock_client = Mock()
                mock_client_contructor.return_value = mock_client
                mock_client.describe_stacks.return_value = input_params
                mock_client.get_parameters.return_value = params_store_output
                # foo.describe_stacks.side_effect = [input_params]
                # foo.get_parameters.side_effect = [params_store_output]

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
        self.assertEqual(self.settings.pcf_pcfprivatesshkey, "-----BEGIN RSA PRIVATE KEY-----foobarabc/q-----END RSA PRIVATE KEY-----")

    def test_parses_environment(self):
        self.assertEqual(self.settings.ops_manager_version, '99.0.1')
        self.assertEqual(self.settings.opsman_url, 'https://opsman.pcf.example.com')

    def test_default_values(self):
        self.assertEqual(self.settings.opsman_user, 'admin')

    def test_get_s3_endpoint(self):
        self.assertEqual(self.settings.get_s3_endpoint(), "s3-canada-west-1.amazonaws.com")

    def test_get_s3_endpoint_east1(self):
        self.settings.region = "us-east-1"
        self.assertEqual(self.settings.get_s3_endpoint(), "s3.amazonaws.com")
