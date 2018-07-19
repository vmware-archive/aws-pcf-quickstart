# aws-pcf-quickstart
#
# Copyright (c) 2017-Present Pivotal Software, Inc. All Rights Reserved.
#
# This program and the accompanying materials are made available under
# the terms of the under the Apache License, Version 2.0 (the "License");
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
import json

from mock import Mock, patch, mock_open

import accept_eula
from settings import Settings


class TestAcceptEULA(unittest.TestCase):
    def setUp(self):
        self.settings = Mock(Settings)
        self.settings.region = 'canada-1a'
        self.settings.pcf_input_pivnettoken = 'MY-TOKEN'
        self.settings.ert_release_id = 1337
        self.settings.stemcell_release_id = 7331

    @patch("util.exponential_backoff_cmd")
    def test_accept_ert_eula_success(self, mock_exponential_backoff_cmd):
        mock_exponential_backoff_cmd.side_effect = [login_success, accept_success]
        result = accept_eula.accept_ert_eula(self.settings)
        self.assertEqual(result, (
            "Success; accepted: https://network.pivotal.io/api/v2/eulas/120 at: 2018-07-19", "", 0))

    @patch("util.exponential_backoff_cmd")
    def test_accept_ert_eula_fail(self, mock_exponential_backoff_cmd):
        mock_exponential_backoff_cmd.side_effect = [login_success, accept_error]
        result = accept_eula.accept_ert_eula(self.settings)
        self.assertEqual(result, (
            "Failed to accept ERT EULA; got message from Pivotal Network: foo error message", "", 1))

    @patch("util.exponential_backoff_cmd")
    def test_accept_stemcell_eula_success(self, mock_exponential_backoff_cmd):
        mock_exponential_backoff_cmd.side_effect = [login_success, accept_success]
        result = accept_eula.accept_stemcell_eula(self.settings)
        self.assertEqual(result, (
            "Success; accepted: https://network.pivotal.io/api/v2/eulas/120 at: 2018-07-19", "", 0))

    @patch("util.exponential_backoff_cmd")
    def test_accept_stemcell_eula_fail(self, mock_exponential_backoff_cmd):
        mock_exponential_backoff_cmd.side_effect = [login_success, accept_error]
        result = accept_eula.accept_stemcell_eula(self.settings)
        self.assertEqual(result, (
            "Failed to accept stemcell EULA; got message from Pivotal Network: foo error message", "", 1))

    @patch("util.exponential_backoff_cmd")
    def test_post_eula_success(self, mock_exponential_backoff_cmd):
        mock_exponential_backoff_cmd.side_effect = [login_success, accept_success]
        result = accept_eula.post_eula(self.settings, 'my-awesome-product', 1337)
        self.assertEqual(result, (
            "accepted: https://network.pivotal.io/api/v2/eulas/120 at: 2018-07-19", "", 0))

    @patch("util.exponential_backoff_cmd")
    def test_post_eula_login_error(self, mock_exponential_backoff_cmd):
        mock_exponential_backoff_cmd.side_effect = [login_error]
        result = accept_eula.post_eula(self.settings, 'my-awesome-product', 1337)
        self.assertEqual(result, (
            "2018/07/19 15:51:00 Exiting with error: failed to fetch API token - received status 401", "", 1))

    @patch("util.exponential_backoff_cmd")
    def test_accept_eulas_accepts_both_eulas(self, mock_exponential_backoff_cmd):
        mock_exponential_backoff_cmd.side_effect = [
            login_success,
            accept_success,
            login_success,
            accept_success,
        ]
        result = accept_eula.accept_eulas(self.settings)
        self.assertEqual(result, (
            "Success; accepted: https://network.pivotal.io/api/v2/eulas/120 at: 2018-07-19", "", 0))


login_success = ("Logged-in successfully", "", 0)
login_error = ("2018/07/19 15:51:00 Exiting with error: failed to fetch API token - received status 401", "", 1)

accept_success = ("""
{
  "_links": {
    "eula": {
      "href": "https://network.pivotal.io/api/v2/eulas/120"
    }
  },
  "accepted_at": "2018-07-19"
}
""", "", 0)

accept_error = ("""
{
  "message": "foo error message",
  "status": 404
}
""", "", 1)
