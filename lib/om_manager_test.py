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

import subprocess
import unittest
from subprocess import Popen

import requests
from mock import Mock, patch

import om_manager
from settings import Settings


class TestOmManager(unittest.TestCase):
    def setUp(self):
        self.settings = Mock(Settings)
        self.settings.opsman_url = 'https://cf.example.com'
        self.settings.opsman_user = 'admin'
        self.settings.pcf_opsmanageradminpassword = 'monkey-123'

    def to_bytes(self, str: str):
        return bytearray(str, "utf-8")

    @patch('subprocess.Popen')
    def test_configure_auth(self, mock_popen):
        p = Mock(Popen)
        mock_popen.return_value = p
        p.returncode = 0
        p.communicate.return_value = self.to_bytes(
            "out: foo"), self.to_bytes("error: bar")
        om_manager.config_opsman_auth(self.settings)
        mock_popen.assert_called_with(
            ["om",
             "-k",
             "--target", "https://cf.example.com",
             "configure-authentication",
             "--username", "admin",
             "--password", "monkey-123",
             "--decryption-passphrase", "monkey-123"],
            stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

    @patch('om_manager.get_om_with_auth')
    @patch('util.run_command')
    def test_curl_get(self, mock_run_command, mock_get_om_with_auth):
        mock_get_om_with_auth.return_value = ["om", "plus", "some", "auth"]
        om_manager.curl_get(self.settings, "/api/foo")

        mock_run_command.assert_called_with(
            ["om",
             "plus", "some", "auth",
             "curl",
             "--path", "/api/foo"])

    @patch('om_manager.get_om_with_auth')
    @patch('util.run_command')
    def test_curl_payload(self, mock_run_command, mock_get_om_with_auth):
        mock_get_om_with_auth.return_value = [
            "om", "-k", "plus", "some", "auth"
        ]

        om_manager.curl_payload(
            self.settings, "/api/foo", '{"foo": "bar"}', "PUT")

        mock_run_command.assert_called_with(
            ["om",
             "-k",
             "plus", "some", "auth",
             "curl",
             "--path", "/api/foo",
             "--request", "PUT",
             "--data", '{\"foo\": \"bar\"}']
        )

    @patch('util.run_command')
    @patch('time.sleep')
    @patch('builtins.print')
    def test_prints_error(self, mock_print, mock_sleep, mock_run_command):
        mock_run_command.return_value = "foo", "bar", 1

        om_manager.config_opsman_auth(self.settings)

        mock_print.assert_called_with("error: bar")

    @patch('subprocess.Popen')
    @patch('time.sleep')
    @patch('builtins.print')
    def test_retries(self, mock_print, mock_sleep, mock_popen):
        errors = ["out: i/o timeout",
                  "connection refused", "yo, no opsman for you"]
        p = Mock(Popen)
        mock_popen.return_value = p
        p.returncode = 1
        for recoverable_error in errors:
            mock_popen.reset_mock()
            p.communicate.return_value = self.to_bytes(
                recoverable_error), self.to_bytes("error: bar")
            om_manager.config_opsman_auth(self.settings)

            self.assertEqual(mock_popen.call_count, 6)

    @patch('subprocess.Popen')
    @patch('time.sleep')
    @patch('builtins.print')
    def test_exponential_backoff(self, mock_print, mock_sleep, mock_popen):
        p = Mock(Popen)
        mock_popen.return_value = p
        p.returncode = 1
        mock_popen.reset_mock()
        p.communicate.return_value = self.to_bytes(
            "out: i/o timeout"), self.to_bytes("error: bar")
        om_manager.config_opsman_auth(self.settings)

        self.assertEqual(mock_sleep.call_count, 5)
        self.assertEqual(mock_sleep.call_args_list[0][0][0], 0)
        self.assertEqual(mock_sleep.call_args_list[1][0][0], 1)
        self.assertEqual(mock_sleep.call_args_list[2][0][0], 8)
        self.assertEqual(mock_sleep.call_args_list[3][0][0], 27)
        self.assertEqual(mock_sleep.call_args_list[4][0][0], 64)

    @patch('util.run_command')
    @patch('time.sleep')
    @patch('builtins.print')
    def test_exponential_backoff_result(self, mock_print, mock_sleep, mock_run_command):
        mock_run_command.return_value = "foo", "bar", 42
        # mock_popen.reset_mock()
        out, err, status_code = om_manager.config_opsman_auth(self.settings)

        self.assertEqual(status_code, 42)
        self.assertEqual(out, "foo")
        self.assertEqual(err, "bar")

    def test_get_om_with_auth(self):
        expected_om_command = ["om",
                               "-k",
                               "--target", "https://cf.example.com",
                               "--username", "admin",
                               "--password", "monkey-123"]
        om_command = om_manager.get_om_with_auth(self.settings)
        self.assertEqual(om_command, expected_om_command)

    @patch('requests.get')
    def test_is_opsman_configured_true(self, mock_requests_get):
        response = Mock(requests.Response)
        response.status_code = 401
        mock_requests_get.return_value = response
        return_value = om_manager.is_opsman_configured(self.settings)
        self.assertEqual(True, return_value)

    @patch('requests.get')
    def test_is_opsman_configured_false(self, mock_requests_get):
        response = Mock(requests.Response)
        response.status_code = 400
        mock_requests_get.return_value = response
        return_value = om_manager.is_opsman_configured(self.settings)
        self.assertEqual(False, return_value)
