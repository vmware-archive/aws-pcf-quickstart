import unittest

from mock import Mock, patch

import configure_ert
from settings import Settings


class TestConfigureERT(unittest.TestCase):
    def setUp(self):
        self.settings = Mock(Settings)
        self.settings.opsman_url = 'https://cf.example.com'
        self.settings.opsman_user = 'admin'
        self.settings.opsman_password = 'monkey-123'
        self.settings.stack_name = 'pcf-to-the-max-stack'
        self.settings.elb_prefix = 'to-the-max'
        self.settings.pcf_input_domain = 'example.com'
        self.settings.pcf_rds_address = 'https://rds.example.com'
        self.settings.pcf_rds_username = 'user'
        self.settings.pcf_rds_password = 'monkey123'
        self.settings.pcf_rds_port = '3306'
        self.settings.admin_email = 'pcf@exmaple.com'
        self.settings.pcf_elastic_runtime_s3_buildpacks_bucket = 'bucket-bp'
        self.settings.pcf_elastic_runtime_s3_droplets_bucket = 'bucket-dp'
        self.settings.pcf_elastic_runtime_s3_packages_bucket = 'bucket-pkg'
        self.settings.pcf_elastic_runtime_s3_resources_bucket = 'bucket-rsc'
        self.settings.pcf_iam_access_key_id = 'key-vale'
        self.settings.pcf_iam_secret_access_key = 'key-secret'
        self.settings.debug = False

    def test_flow(self):
        with patch('om_manager.stage_product') as mock_stage:
            mock_stage.return_value = 0
            with patch('configure_ert.configure_tile_az') as mock_az:
                mock_az.return_value = 0
                with patch('configure_ert.configure_ert_config') as mock_config:
                    mock_config.return_value = 1
                    with patch('configure_ert.configure_ert_resources') as mock_resources:
                        mock_resources.return_value = 0
                        exit_code = configure_ert.configure_ert(self.settings)

                        mock_stage.assert_called()
                        mock_az.assert_called()
                        mock_config.assert_called()
                        mock_resources.assert_not_called()
                        self.assertEqual(1, exit_code)

    @patch('om_manager.exponential_backoff')
    @patch('settings.get_om_with_auth')
    def test_configure_ert_resources(self, mock_util_get_om_with_auth, mock_backoff):
        mock_util_get_om_with_auth.return_value = "foo"
        configure_ert.configure_ert_resources(self.settings)

        cmd = mock_backoff.call_args[0][0]
        self.assertTrue(cmd.startswith("foo configure-product -n cf -pr"))

    @patch('om_manager.exponential_backoff')
    @patch('settings.get_om_with_auth')
    def test_configure_ert_config(self, mock_util_get_om_with_auth, mock_backoff):
        mock_util_get_om_with_auth.return_value = "foo"
        configure_ert.configure_ert_config(self.settings)
        cmd = mock_backoff.call_args[0][0]
        self.assertTrue(cmd.startswith("foo configure-product -n cf -p '{"))
