# pivotal-cloud-foundry-quickstart
#
# Copyright (c) 2017-Present Pivotal Software, Inc. All Rights Reserved.
#
# This program and the accompanying materials are made available under
# the terms of the under the Apache License, Version 2.0 (the "License”);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

import requests
from mock import Mock, patch, mock_open

import accept_eula
from settings import Settings


class TestAcceptEULA(unittest.TestCase):
    def setUp(self):
        self.settings = Mock(Settings)
        self.settings.region = 'canada-1a'
        self.settings.pcf_input_pivnettoken = 'MY-TOKEN'
        self.settings.ert_release_id = 1337

    @patch("util.exponential_backoff")
    def test_accept_ert_eula_success(self, mock_exponential_backoff):
        response = Mock(requests.Response)
        response.status_code = 200
        mock_exponential_backoff.return_value = (response, accept_eula.EULAResult.SUCCESS)
        result = accept_eula.accept_ert_eula(self.settings)
        self.assertEqual(result, ("Success", "", 0))

    @patch("util.exponential_backoff")
    def test_accept_ert_eula_fail(self, mock_exponential_backoff):
        response = Mock(requests.Response)
        response.status_code = 503
        mock_exponential_backoff.return_value = (response, accept_eula.EULAResult.RETRY)

        result = accept_eula.accept_ert_eula(self.settings)
        self.assertEqual(result[2], 1)

    @patch('requests.post')
    def test_post_eula_success(self, mock_requests_post):
        response = Mock(requests.Response)
        response.status_code = 200
        mock_requests_post.return_value = response

        result = accept_eula.post_eula(self.settings, 1337)

        self.assertEqual(result[0], response)
        self.assertEqual(result[1], accept_eula.EULAResult.SUCCESS)

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

        self.assertEqual(result[0], response)
        self.assertEqual(result[1], accept_eula.EULAResult.FAILURE)

    @patch('requests.post')
    def test_post_eula_pivnet_failure(self, mock_requests_post):
        response = Mock(requests.Response)
        response.status_code = 502
        mock_requests_post.return_value = response

        result = accept_eula.post_eula(self.settings, 1337)

        self.assertEqual(result[0], response)
        self.assertEqual(result[1], accept_eula.EULAResult.RETRY)

    @patch('accept_eula.post_eula')
    @patch('time.sleep')
    def test_exponential_backoff(self, mock_sleep, mock_post_eula):
        retry_response = Mock(requests.Response)
        retry_response.status_code = 502
        success_response = Mock(requests.Response)
        success_response.status_code = 200

        mock_post_eula.side_effect = [
            (retry_response, accept_eula.EULAResult.RETRY),
            (retry_response, accept_eula.EULAResult.RETRY),
            (success_response, accept_eula.EULAResult.SUCCESS)
        ]

        result = accept_eula.accept_ert_eula(self.settings)

        self.assertEqual(mock_sleep.call_count, 2)
        self.assertEqual(result[0], "Success")
        self.assertEqual(result[2], 0)


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
