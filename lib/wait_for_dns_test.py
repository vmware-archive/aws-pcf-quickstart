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

import socket
import unittest

from mock import Mock, patch

import wait_for_dns
from settings import Settings


class TestWaitCondition(unittest.TestCase):
    def setUp(self):
        self.settings = Mock(Settings)
        self.settings.region = 'canada-1a'
        self.settings.pcf_pcfopsmanagerinstanceip = '192.168.1.1'
        self.settings.debug = False

    @patch('socket.gethostbyname')
    def test_check_dns_lookup_success(self, mock_gethostbyname):
        mock_gethostbyname.return_value = "192.168.1.1"
        result = wait_for_dns.check_dns("foo.example.com")

        self.assertEqual(result, "192.168.1.1")

    @patch('socket.gethostbyname')
    def test_check_dns_lookup_failure(self, mock_gethostbyname):
        mock_gethostbyname.side_effect = socket.gaierror()
        result = wait_for_dns.check_dns("foo.example.com")

        self.assertEqual(result, "")

    @patch('time.sleep')
    @patch('wait_for_dns.check_dns')
    def test_wait_sleep(self, mock_check_dns, mock_sleep):
        mock_check_dns.side_effect = [
            "",
            "",
            "192.168.1.1"
        ]

        wait_for_dns.wait_for_dns(self.settings)

        self.assertEqual(mock_sleep.call_count, 2)
