import unittest

import requests
from mock import Mock, patch, mock_open

import accept_eula
from settings import Settings


class TestAcceptEULA(unittest.TestCase):
    def setUp(self):
        self.settings = Mock(Settings)
        self.settings.region = 'canada-1a'
        self.settings.debug = False
        self.settings.pcf_input_pivnettoken = 'MY-TOKEN'

    def test_get_release_id(self):
        my_mock_open = mock_open(read_data=metadata_json)
        with patch('accept_eula.open', my_mock_open):
            release_id = accept_eula.get_release_id()
        self.assertEqual(5334, release_id)
        my_mock_open.assert_called_with('/home/ubuntu/tiles/ert-metadata.json', 'r')

    @patch("accept_eula.exponential_backoff")
    @patch("accept_eula.get_release_id")
    def test_accept_ert_eula_success(self, mock_get_release_id, mock_exponential_backoff):
        mock_get_release_id.return_value = 1337
        mock_exponential_backoff.return_value = accept_eula.EULAResult.SUCCESS

        self.assertEqual(0, accept_eula.accept_ert_eula(self.settings))

    @patch("accept_eula.exponential_backoff")
    @patch("accept_eula.get_release_id")
    def test_accept_ert_eula_fail(self, mock_get_release_id, mock_exponential_backoff):
        mock_get_release_id.return_value = 1337
        mock_exponential_backoff.return_value = accept_eula.EULAResult.RETRY

        self.assertEqual(1, accept_eula.accept_ert_eula(self.settings))

    @patch('requests.post')
    def test_post_eula_success(self, mock_requests_post):
        response = Mock(requests.Response)
        response.status_code = 200
        mock_requests_post.return_value = response

        result = accept_eula.post_eula(self.settings, 1337)

        self.assertEqual(result, accept_eula.EULAResult.SUCCESS)

        expected_headers = {
            'Authorization': 'Token MY-TOKEN',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'PCF-Ecosystem-AWS-client'
        }

        mock_requests_post.assert_called_with(
            url='https://network.pivotal.io/api/v2/products/elastic-runtime/releases/1337/eula_acceptance',
            headers=expected_headers
        )

    @patch('requests.post')
    def test_post_eula_failure(self, mock_requests_post):
        response = Mock(requests.Response)
        response.status_code = 401
        mock_requests_post.return_value = response

        result = accept_eula.post_eula(self.settings, 1337)

        self.assertEqual(result, accept_eula.EULAResult.FAILURE)

    @patch('requests.post')
    def test_post_eula_pivnet_failure(self, mock_requests_post):
        response = Mock(requests.Response)
        response.status_code = 502
        mock_requests_post.return_value = response

        result = accept_eula.post_eula(self.settings, 1337)

        self.assertEqual(result, accept_eula.EULAResult.RETRY)

    @patch('accept_eula.post_eula')
    @patch('time.sleep')
    def test_exponential_backoff(self, mock_sleep, mock_post_eula):
        mock_post_eula.side_effect = [
            accept_eula.EULAResult.RETRY,
            accept_eula.EULAResult.RETRY,
            accept_eula.EULAResult.SUCCESS
        ]

        result = accept_eula.exponential_backoff(self.settings, 1337)

        self.assertEqual(result, accept_eula.EULAResult.SUCCESS)
        self.assertEqual(mock_sleep.call_count, 2)


metadata_json = """
{
  "Release": {
    "ID": 5334,
    "Version": "1.10.8",
    "ReleaseType": "Security Release",
    "EULASlug": "pivotal_software_eula",
    "ReleaseDate": "2017-05-04",
    "Description": "Please refer to the release notes",
    "ReleaseNotesURL": "https://docs.pivotal.io/pivotalcf/1-10/pcf-release-notes/runtime-rn.html",
    "Availability": "All Users",
    "UserGroupIDs": null,
    "Controlled": true,
    "ECCN": "5D002",
    "LicenseException": "ENC",
    "EndOfSupportDate": "2017-12-31",
    "EndOfGuidanceDate": "",
    "EndOfAvailabilityDate": "",
    "ProductFiles": [
      {
        "ID": 18379
      },
      {
        "ID": 19963
      },
      {
        "ID": 19960
      }
    ]
  },
  "ProductFiles": [
    {
      "File": "PCF Elastic Runtime 1.10 License",
      "Description": "",
      "UploadAs": "",
      "AWSObjectKey": "product-files/elastic-runtime/open_source_license_PCF-Elastic-Runtime_-_1.10_-_GA.txt",
      "FileType": "Open Source License",
      "FileVersion": "1.0",
      "SHA256": "",
      "MD5": "",
      "ID": 18379,
      "Version": "",
      "DocsURL": "",
      "SystemRequirements": [],
      "Platforms": null,
      "IncludedFiles": []
    },
    {
      "File": "PCF Cloudformation for AWS Setup",
      "Description": "",
      "UploadAs": "",
      "AWSObjectKey": "product-files/elastic-runtime/pcf_1.10.8-build.7_cloudformation.json",
      "FileType": "Software",
      "FileVersion": "1.10.8-build.7",
      "SHA256": "c5c044036453d1cf21b9c7cab91a4e5c9544fc10d36088016f4b161afc92e137",
      "MD5": "",
      "ID": 19963,
      "Version": "",
      "DocsURL": "",
      "SystemRequirements": [],
      "Platforms": null,
      "IncludedFiles": []
    },
    {
      "File": "PCF Elastic Runtime",
      "Description": "",
      "UploadAs": "",
      "AWSObjectKey": "product-files/elastic-runtime/cf-1.10.8-build.7.pivotal",
      "FileType": "Software",
      "FileVersion": "1.10.8-build.7",
      "SHA256": "70070bf22231d9971c97b8deb8c4cd5ba990d24101e5398d0ccc70778060dbea",
      "MD5": "",
      "ID": 19960,
      "Version": "",
      "DocsURL": "",
      "SystemRequirements": [],
      "Platforms": null,
      "IncludedFiles": []
    }
  ],
  "Dependencies": [],
  "DependencySpecifiers": [],
  "UpgradePaths": [],
  "UpgradePathSpecifiers": [],
  "FileGroups": null
}
"""
