import unittest

import boto3
import tempfile
from mock import Mock, patch, mock_open

import download_tiles
from settings import Settings


class TestProgressPercentage(unittest.TestCase):
    @patch('builtins.print')
    def test_prints_percent(self, mock_print):
        p = download_tiles.ProgressPercentage('my-file-name')
        p(0)
        p(5 * 1024 * 1024)
        p(5 * 1024 * 1024)

        self.assertEqual(mock_print.call_count, 0)

        p(5 * 1024 * 1024)

        self.assertEqual(mock_print.call_count, 1)
        self.assertEqual(mock_print.call_args_list[0][0][0], "my-file-name --> 15.0 MB transferred")


class TestDownloadTiles(unittest.TestCase):
    def setUp(self):
        self.settings = Mock(Settings)
        self.settings.tile_bucket_s3_name = 'my-bucket'
        self.settings.tile_bucket_s3_access_key = 'my-access-key'
        self.settings.tile_bucket_s3_secret_access_key = 'my-access-secret'
        self.settings.tile_bucket_region = 'canada-1'
        self.settings.aws_broker_version = 'canada-1'
        self.settings.ert_version = '1.99.1'

    @patch('boto3.client')
    @patch('download_tiles.download_tile')
    def test_download_tiles_aborts_on_failure(self, mock_download_tile, mock_client):
        mock_download_tile.return_value = 127

        returncode = download_tiles.download_tiles(self.settings)

        self.assertEqual(mock_download_tile.call_count, 1)
        self.assertEqual(returncode, 127)

    @patch('boto3.client')
    @patch('download_tiles.download_tile')
    def test_download_tiles(self, mock_download_tile, mock_client):
        mock_download_tile.return_value = 0
        returncode = download_tiles.download_tiles(self.settings)

        self.assertEqual(mock_download_tile.call_count, 3)
        self.assertEqual(returncode, 0)

    @patch("download_tiles.verify_sha256")
    def test_download_tile(self, mock_verify):
        client = boto3.client('s3')
        mock_s3 = Mock(client)

        my_mock_open = mock_open(read_data="")
        with patch('download_tiles.open', my_mock_open):
            with patch('download_tiles.ProgressPercentage') as mock_callback:
                download_tiles.download_tile(
                    'my-tile.pivotal', self.settings, mock_s3
                )

        self.assertEqual(mock_s3.download_file.call_count, 2)
        mock_s3.download_file.assert_called_with(
            "my-bucket", "my-tile.pivotal", "/tmp/my-tile.pivotal",
            Callback=mock_callback()
        )

    def test_verify_sha256(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"Hello World!\n")
            print(f.name)

        sha256 = '03ba204e50d126e4674c005e04d82e84c21366780af1f43bd54a37816b6ab340'
        returncode = download_tiles.verify_sha256(f.name, sha256)
        self.assertEqual(returncode, 0)
