import unittest

import boto3
import botocore.session
from botocore.stub import Stubber, ANY
from mock import Mock

import download_tiles
import io

from settings import Settings


class TestDownloadTiles(unittest.TestCase):
    def setUp(self):
        self.settings = Mock(Settings)
        # self.settings.zones = ["zone1"]
        # self.settings.pcf_iam_access_key_id = "access_id"
        # self.settings.pcf_iam_secret_access_key = "secret_key"
        # self.settings.vpc_id = "vpc-123"
        # self.settings.security_group = "sec-123"
        # self.settings.key_pair_name = "mytestkeypair"
        # self.settings.ssh_private_key = "private key"
        # self.settings.region = "region-123"
        # self.settings.vpc_private_subnet_id = "subnet1"
        # self.settings.vpc_private_subnet_az = "east1"
        # self.settings.vpc_private_subnet_id2 = "subnet2"
        # self.settings.vpc_private_subnet_az2 = "east2"
        # self.settings.opsman_url = "https://example123.com"
        # self.settings.opsman_password = "monkey123"
        # self.settings.opsman_user = "testuser"
        # self.settings.debug = False
        self.settings.tile_bucket_s3_name='my-bucket'
        self.settings.tile_bucket_s3_access_key='my-access-key'
        self.settings.tile_bucket_s3_secret_access_key='my-access-secret'
        self.settings.ert_version='1.99.1'


    def x_test_download_ert(self):
        s3 = boto3.client('s3')
        stubber = Stubber(s3)
        stubber.add_client_error(
            'download_fileobj', service_error_code='Forbidden', http_status_code=403
        )
        stubber.activate()

        download_tiles.download_ert(s3, self.settings)


    def test_why_mock_does_not_work(self):
        # s3 = boto3.client('s3')
        s3 = botocore.session.get_session().create_client('s3')

        stubber = Stubber(s3)

        stubber.add_client_error(
            'download_fileobj', service_error_code='403', service_message='Forbidden', http_status_code=403,
            service_error_meta=None, expected_params=ANY
        )
        stubber.activate()

        output = io.StringIO()
        s3.download_fileobj('foo', 'bar', output)


    def test_error_handling_on_auth_failure(self):
        pass
