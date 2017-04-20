import os
import unittest

from mock import patch, mock_open

import settings


class TestSettings(unittest.TestCase):
    def setUp(self):
        my_mock_open = mock_open(read_data="""
{"Stacks": [{
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
""")

        os.environ['DNS_SUFFIX'] = 'example.com'
        os.environ['OPS_MANAGER_VERSION'] = '99.0.1'
        os.environ['OPS_MANAGER_URL'] = 'https://some-random-ec2-domain.example.com'
        os.environ['OPS_MANAGER_ADMIN_PASSWORD'] = 'monkey123'
        os.environ["SSH_PRIVATE_KEY"] = "my-key-value-asdf-1234"
        os.environ["REGION"] = "canada-1"
        os.environ["ERT_VERSION"] = "1.2.3"
        os.environ["TILE_BUCKET_S3_NAME"] = "my-bucket"
        os.environ["TILE_BUCKET_S3_ACCESS_KEY"] = "my-access-key"
        os.environ["TILE_BUCKET_S3_SECRET_ACCESS_KEY"] = "my-access-secret"

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
