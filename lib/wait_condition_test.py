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
        self.settings.debug = False

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
