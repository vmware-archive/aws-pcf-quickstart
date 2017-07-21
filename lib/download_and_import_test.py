import unittest

import tempfile
from mock import patch, Mock

import download_and_import
import om_manager
import settings


class TestDownloadAndImport(unittest.TestCase):
    def setUp(self):
        om_manager.debug_mode = False

        self.settings = Mock(settings.Settings)
        self.settings.debug = False

    @patch('util.exponential_backoff_cmd')
    @patch('download_and_import.do_pivnet_download')
    def test_download_asset_success(self, mock_do_pivnet_download, mock_util):
        mock_do_pivnet_download.return_value = "", "", 0

        out, err, exit_code = download_and_import.download_assets(self.settings, '/home/ubuntu/tiles/')

        self.assertEqual(mock_do_pivnet_download.call_count, 2)
        self.assertEqual(exit_code, 0)

        self.assertEqual(mock_do_pivnet_download.mock_calls[0][1][0], 'stemcells')
        self.assertEqual(mock_do_pivnet_download.mock_calls[1][1][0], 'cf')

    @patch('util.exponential_backoff_cmd')
    @patch('download_and_import.do_pivnet_download')
    def test_download_asset_failure(self, mock_do_pivnet_download, mock_util):
        mock_do_pivnet_download.return_value = "download failed", "", 1

        out, err, exit_code = download_and_import.download_assets(self.settings, '/home/ubuntu/tiles/')

        self.assertEqual(mock_do_pivnet_download.call_count, 1)
        self.assertEqual(out, "download failed")
        self.assertEqual(exit_code, 1)

    @patch('util.exponential_backoff_cmd')
    @patch('download_and_import.verify_sha256')
    @patch('glob.glob')
    def test_do_pivnet_download_success(self, mock_os_listdir, mock_verify_sha256, mock_util):
        mock_util.return_value = "", "", 0
        mock_os_listdir.return_value = ['/home/ubuntu/tiles/cf-1.9.0.pivotal']
        mock_verify_sha256.return_value = 0

        download_and_import.do_pivnet_download('cf', '1.9.0', 'cf*.pivotal', 'xyz123', '/home/ubuntu/tiles/')

        mock_verify_sha256.assert_called_with('/home/ubuntu/tiles/cf-1.9.0.pivotal', 'xyz123')

    def test_verify_sha256_match(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_name = "{}/foo.txt".format(temp_dir)
            with open(file_name, 'w') as f:
                f.write('Test\n')
                f.write('foo bar\n')

            result = download_and_import.verify_sha256(
                file_name, '9e7e95359fb81b4089289d58f9a38ff37d744db7c5941a156ff23216706da8cd'
            )

        self.assertEqual(result, 0)

    def test_verify_sha256_no_match(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_name = "{}/foo.txt".format(temp_dir)
            with open(file_name, 'w') as f:
                f.write('Test\n')
                f.write('foo bar baz\n')

            result = download_and_import.verify_sha256(
                file_name, '9e7e95359fb81b4089289d58f9a38ff37d744db7c5941a156ff23216706da8cd'
            )

        self.assertEqual(result, 1)

    @patch('util.exponential_backoff_cmd')
    @patch('om_manager.get_om_with_auth')
    @patch('os.listdir')
    def test_upload_assets_success(self, mock_os_listdir, mock_get_om_with_auth, mock_util):
        mock_os_listdir.return_value = ['tile.pivotal', 'stemcell.tgz', 'password.txt', 'secondtile.pivotal']
        mock_get_om_with_auth.return_value = "om -u username -p password"
        mock_util.return_value = "", "", 0
        out, err, exit_code = download_and_import.upload_assets(self.settings, "/home/ubuntu/tiles")

        self.assertEqual(exit_code, 0)
        self.assertEqual(mock_util.call_count, 2)

    @patch('util.exponential_backoff_cmd')
    @patch('om_manager.get_om_with_auth')
    @patch('os.listdir')
    def test_upload_stemcell_success(self, mock_os_listdir, mock_get_om_with_auth, mock_util):
        mock_os_listdir.return_value = ['tile.pivotal', 'stemcell.tgz', 'password.txt', 'secondtile.pivotal']
        mock_get_om_with_auth.return_value = "om -u username -p password"
        mock_util.return_value = "", "", 0
        out, err, exit_code = download_and_import.upload_stemcell(self.settings, "/home/ubuntu/tiles")

        self.assertEqual(exit_code, 0)
        self.assertEqual(mock_util.call_count, 1)

    @patch('util.exponential_backoff_cmd')
    @patch('om_manager.get_om_with_auth')
    @patch('os.listdir')
    def test_upload_stemcell_failure(self, mock_os_listdir, mock_get_om_with_auth, mock_util):
        mock_os_listdir.return_value = ['tile.pivotal', 'stemcell.tgz', 'password.txt', 'secondtile.pivotal']
        mock_get_om_with_auth.return_value = "om -u username -p password"
        mock_util.return_value = "icky stemcell", "", 1
        out, err, exit_code = download_and_import.upload_stemcell(self.settings, "/home/ubuntu/tiles")

        self.assertEqual(exit_code, 1)
        self.assertEqual(mock_util.call_count, 1)
        self.assertEqual(out, "icky stemcell")
