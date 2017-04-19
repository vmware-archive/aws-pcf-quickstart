import unittest

from mock import Mock, patch

import configure_opsman_director
from settings import Settings


class TestConfigureOpsManDirector(unittest.TestCase):
    def setUp(self):
        self.settings = Mock(Settings)
        self.settings.zones = ["zone1"]
        self.settings.pcf_iam_access_key_id = "access_id"
        self.settings.pcf_iam_secret_access_key = "secret_key"
        self.settings.vpc_id = "vpc-123"
        self.settings.security_group = "sec-123"
        self.settings.key_pair_name = "mytestkeypair"
        self.settings.ssh_private_key = "private key"
        self.settings.region = "region-123"
        self.settings.vpc_private_subnet_id = "subnet1"
        self.settings.vpc_private_subnet_az = "east1"
        self.settings.vpc_private_subnet_id2 = "subnet2"
        self.settings.vpc_private_subnet_az2 = "east2"
        self.settings.opsman_url = "https://example123.com"
        self.settings.opsman_password = "monkey123"
        self.settings.opsman_user = "testuser"
        self.settings.debug = False

    def test_flow(self):
        with patch('om_manager.run_command') as mock_run_command:
            mock_run_command.side_effect = [("", "", 0), ("", "", 0), ("", "", 1)]
            exit_code = configure_opsman_director.configure_opsman_director(self.settings)

            self.assertEqual(exit_code, 1)
            self.assertEqual(mock_run_command.call_count, 3)

    def test_fully_configures(self):
        with patch('settings.get_om_with_auth') as mock_util_get_om_with_auth:
            mock_util_get_om_with_auth.return_value = "foo"
            with patch('om_manager.run_command') as mock_call:
                mock_call.return_value = ("", "", 0)
                exit_code = configure_opsman_director.configure_opsman_director(self.settings)

                self.assertEqual(mock_call.call_count, 5)
                self.assertEqual(exit_code, 0)

                calls = mock_call.call_args_list
                self.assertTrue(calls[0][0][0].startswith("foo configure-bosh --iaas-configuration '{"))
                self.assertTrue(calls[1][0][0].startswith("foo configure-bosh --director-configuration '{"))
                self.assertTrue(calls[2][0][0].startswith("foo configure-bosh --az-configuration '{"))
                self.assertTrue(calls[3][0][0].startswith("foo configure-bosh --networks-configuration '{"))
                self.assertTrue(calls[4][0][0].startswith("foo configure-bosh --network-assignment '{"))
