import unittest

from mock import patch, mock_open, Mock

class TestDownloadAndImport(unittest.TestCase):

    @patch('download_and_import.do_pivnet_download')
    def test_download_asset_success(self, mock_do_pivnet_download):
        mock_do_pivnet_download.return_value = "", "", 0

    @patch('download_and_import.do_pivnet_download')
    def test_download_asset_success(self, mock_do_pivnet_download):
        mock_do_pivnet_download.return_value = "", "", 0


