import os
import unittest

import settings


class TestSettings(unittest.TestCase):
    def setUp(self):
        os.environ['ERT_SQL_DB_USERNAME'] = 'db-admin'
        os.environ['ERT_SQL_DB_PASSWORD'] = 'abc123'
        os.environ['DNS_SUFFIX'] = 'example.com'
        os.environ['OPS_MANAGER_VERSION'] = '99.0.1'
        os.environ['OPS_MANAGER_URL'] = 'https://some-random-ec2-domain.example.com'
        os.environ['OPS_MANAGER_ADMIN_PASSWORD'] = 'monkey123'

        self.settings = settings.Settings()

    def test_parses_environment(self):
        self.assertEqual(self.settings.ert_sql_db_username, 'db-admin')
        self.assertEqual(self.settings.ert_sql_db_password, 'abc123')
        self.assertEqual(self.settings.dns_suffix, 'example.com')
        self.assertEqual(self.settings.ops_manager_version, '99.0.1')
        self.assertEqual(self.settings.opsman_url, 'https://some-random-ec2-domain.example.com')

        self.assertEqual(self.settings.opsman_password, 'monkey123')

    def test_default_values(self):
        self.assertEqual(self.settings.opsman_user, 'admin')

    def test_get_om_with_auth(self):
        expected_om_command = "om -k --target https://some-random-ec2-domain.example.com --username 'admin' --password 'monkey123'"
        om_command = settings.get_om_with_auth(self.settings)
        self.assertEqual(om_command, expected_om_command)
