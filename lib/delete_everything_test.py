import unittest

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

    @patch('boto3.client')
    @patch('om_manager.exponential_backoff')
    @patch('om_manager.get_om_with_auth')
    def test_om_delete_installation(self, mock_auth, mock_backoff, mock_client_constructor):
        mock_backoff.return_value = 0
        mock_auth.return_value = "om-with-auth-for-realz"

        delete_everything.delete_everything(self.settings)

        mock_backoff.assert_called_with(
            "om-with-auth-for-realz delete-installation", False
        )

    @patch('boto3.client')
    @patch('om_manager.exponential_backoff')
    @patch('om_manager.get_om_with_auth')
    def test_om_delete_installation_fails(self, mock_auth, mock_backoff, mock_client_constructor):
        mock_backoff.return_value = 1
        mock_client = Mock()
        mock_client_constructor.return_value = mock_client

        return_code = delete_everything.delete_everything(self.settings)

        self.assertEqual(return_code, 1)
        mock_client.delete_bucket.assert_not_called()

    @patch('boto3.client')
    @patch('om_manager.exponential_backoff')
    @patch('om_manager.get_om_with_auth')
    def test_delete_buckets(self, mock_auth, mock_backoff, mock_client_constructor):
        mock_backoff.return_value = 0
        mock_client = Mock()
        mock_client_constructor.return_value = mock_client

        delete_everything.delete_everything(self.settings)

        self.assertEqual(mock_client.delete_bucket.call_count, 4)
        mock_client.delete_bucket.assert_called_with(
            Bucket="bucket-rsc"
        )

    @patch('boto3.client')
    @patch('om_manager.exponential_backoff')
    @patch('om_manager.get_om_with_auth')
    def test_delete_buckets_fails(self, mock_auth, mock_backoff, mock_client_constructor):
        mock_backoff.return_value = 0
        mock_client = Mock()
        mock_client_constructor.return_value = mock_client

        mock_client.delete_bucket.side_effect = ValueError("Nope")

        return_code = delete_everything.delete_everything(self.settings)

        self.assertEqual(mock_client.delete_bucket.call_count, 1)

        self.assertEqual(return_code, 1)
