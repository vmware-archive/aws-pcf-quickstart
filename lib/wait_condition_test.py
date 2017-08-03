# aws-pcf-quickstart
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

import json
import unittest

from mock import Mock, patch

import wait_condition
from settings import Settings


class TestWaitCondition(unittest.TestCase):
    def setUp(self):
        self.settings = Mock(Settings)
        self.settings.region = 'canada-1a'
        self.settings.pcf_pcfwaithandle = 'https://wait.example.com?signature=foo'

    @patch('requests.put')
    def test_report_status(self, mock_put):
        return_code = wait_condition.report_success(self.settings, "Niiiice")

        self.assertEqual(return_code, 0)
        self.assertEqual(mock_put.call_count, 1)

        call_args = mock_put.call_args[1]
        self.assertEqual(call_args.get('params'), "signature=foo")
        self.assertEqual(call_args.get('url'), "https://wait.example.com")

        payload = json.loads(call_args.get("data").decode('utf-8'))
        self.assertEqual(payload.get("Status"), "SUCCESS")
        self.assertEqual(payload.get("Reason"), "Niiiice")
        self.assertEqual(payload.get("Data"), "Niiiice")

    @patch('wait_condition.report_status')
    def test_report_success(self, mock_report_status):
        wait_condition.report_success(self.settings, 'Foo')

        mock_report_status.assert_called_with(self.settings, 'Foo', 'SUCCESS')

    @patch('wait_condition.report_status')
    def test_report_failure(self, mock_report_status):
        wait_condition.report_failure(self.settings, 'Bar')

        mock_report_status.assert_called_with(self.settings, 'Bar', 'FAILURE')
