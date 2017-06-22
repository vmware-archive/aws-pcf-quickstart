import json
import unittest
import socket

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
