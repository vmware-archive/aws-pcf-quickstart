import json
import unittest

import os
from mock import patch, mock_open

import settings


class TestSettings(unittest.TestCase):
    def setUp(self):
        self.pcf_json = """
{"Stacks": [{
      "StackId": "arn:aws:cloudformation:us-west-2:277693604504:stack/pcf-try-again/36ac83b0-2a08-11e7-9a53-500c314110fd",
      "Outputs": [
        {
          "OutputValue": "db-admin",
          "OutputKey": "PcfRdsUsername"
        },{
          "OutputValue": "abc123",
          "OutputKey": "PcfRdsPassword"
        },{
          "OutputValue": "iam-user-key",
          "OutputKey": "PcfIamUserAccessKey"
        },{
          "OutputValue": "iam-secret-key",
          "OutputKey": "PcfIamUserSecretAccessKey"
        },{
          "OutputValue": "vpc-foo",
          "OutputKey": "PcfVpc"
        },{
          "OutputValue": "security-group-id",
          "OutputKey": "PcfVmsSecurityGroupId"
        },{
          "OutputValue": "canada-1b",
          "OutputKey": "PcfPrivateSubnet2AvailabilityZone"
        },{
          "OutputValue": "canada-1a",
          "OutputKey": "PcfPrivateSubnetAvailabilityZone"
        }
      ],
      "Parameters": [
        {
          "ParameterValue": "my-key-pair",
          "ParameterKey": "01NATKeyPair"
        }
      ]
}]}
"""
        my_mock_open = mock_open(read_data=self.pcf_json)

        os.environ['DNS_SUFFIX'] = 'example.com'
        os.environ['OPS_MANAGER_VERSION'] = '99.0.1'
        os.environ['OPS_MANAGER_URL'] = 'https://some-random-ec2-domain.example.com'
        os.environ['OPS_MANAGER_ADMIN_PASSWORD'] = 'monkey123'
        os.environ["SSH_PRIVATE_KEY"] = "my-key-value-asdf-1234"
        os.environ["REGION"] = "canada-1"
        os.environ["ERT_VERSION"] = "1.2.3"
        os.environ["AWS_BROKER_VERSION"] = "4.5.6"
        os.environ["TILE_BUCKET_S3_NAME"] = "my-bucket"
        os.environ["TILE_BUCKET_S3_ACCESS_KEY"] = "my-access-key"
        os.environ["TILE_BUCKET_S3_SECRET_ACCESS_KEY"] = "my-access-secret"
        os.environ["TILE_BUCKET_REGION"] = "canada-1"

        with patch('settings.open', my_mock_open):
            self.settings = settings.Settings()

    def test_parses_environment(self):
        self.assertEqual(self.settings.dns_suffix, 'example.com')
        self.assertEqual(self.settings.ops_manager_version, '99.0.1')
        self.assertEqual(self.settings.opsman_url, 'https://some-random-ec2-domain.example.com')
        self.assertEqual(self.settings.ssh_private_key, 'my-key-value-asdf-1234')
        self.assertEqual(self.settings.region, 'canada-1')

        self.assertEqual(self.settings.opsman_password, 'monkey123')

    def test_parses_stack_output_json(self):
        self.assertEqual(self.settings.ert_sql_db_username, 'db-admin')
        self.assertEqual(self.settings.ert_sql_db_password, 'abc123')
        self.assertEqual(self.settings.pcf_iam_access_key_id, 'iam-user-key')
        self.assertEqual(self.settings.pcf_iam_secret_access_key, 'iam-secret-key')
        self.assertEqual(self.settings.vpc_id, 'vpc-foo')
        self.assertEqual(self.settings.security_group, 'security-group-id')
        self.assertEqual(self.settings.zones, [
            "canada-1a", "canada-1b"
        ])

    def test_parses_stack_paramater_json(self):
        self.assertEqual(self.settings.key_pair_name, 'my-key-pair')

    def test_default_values(self):
        self.assertEqual(self.settings.opsman_user, 'admin')

    def test_get_om_with_auth(self):
        expected_om_command = "om -k --target https://some-random-ec2-domain.example.com --username 'admin' --password 'monkey123'"
        om_command = settings.get_om_with_auth(self.settings)
        self.assertEqual(om_command, expected_om_command)

    def test_get_stack_region(self):
        self.assertEqual(self.settings.get_stack_region(), "us-west-2")

    def test_get_stack_region_bad_input(self):
        new_json = json.loads(self.pcf_json)
        new_json["Stacks"][0]["StackId"] = "foo:bar:yo"
        self.pcf_json = json.dumps(new_json)
        my_mock_open = mock_open(read_data=self.pcf_json)
        with patch('settings.open', my_mock_open):
            self.settings = settings.Settings()
        self.assertRaises(ValueError, self.settings.get_stack_region)

    def test_get_s3_endpoint(self):
        self.assertEqual(self.settings.get_s3_endpoint(), "s3-us-west-2.amazonaws.com")

    def test_get_s3_endpoint_east1(self):
        new_json = json.loads(self.pcf_json)
        new_json["Stacks"][0]["StackId"] = "arn:aws:cloudformation:us-east-1:277693604504:stack/pcf-try-again/36ac83b0-2a08-11e7-9a53-500c314110fd"
        self.pcf_json = json.dumps(new_json)
        my_mock_open = mock_open(read_data=self.pcf_json)
        with patch('settings.open', my_mock_open):
            self.settings = settings.Settings()
        self.assertEqual(self.settings.get_s3_endpoint(), "s3.amazonaws.com")
