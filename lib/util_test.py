import unittest

from mock import Mock, patch

from util import exponential_backoff


class TestUtil(unittest.TestCase):
    @patch('time.sleep')
    def test_exponential_backoff_failing(self, mock_sleep):
        test = Mock()
        test.return_value = 1
        exit_code = exponential_backoff(test, check_fun_test)

        self.assertEqual(mock_sleep.call_count, 5)
        self.assertEqual(mock_sleep.call_args_list[0][0][0], 0)
        self.assertEqual(mock_sleep.call_args_list[1][0][0], 1)
        self.assertEqual(mock_sleep.call_args_list[2][0][0], 8)
        self.assertEqual(mock_sleep.call_args_list[3][0][0], 27)
        self.assertEqual(mock_sleep.call_args_list[4][0][0], 64)

        self.assertEqual(exit_code, 1)

    @patch('time.sleep')
    def test_exponential_backoff_success(self, mock_sleep):
        test = Mock()
        test.return_value = 0
        exit_code = exponential_backoff(test, check_fun_test)
        mock_sleep.assert_not_called()
        self.assertEqual(exit_code, 0)

    @patch('time.sleep')
    def test_exponential_backoff_success_after_failure(self, mock_sleep):
        fake_fun = Mock()
        fake_fun.side_effect = [1, 1, 0]
        exit_code = exponential_backoff(fake_fun, check_fun_test)

        self.assertEqual(mock_sleep.call_count, 2)
        self.assertEqual(exit_code, 0)

    @patch('time.sleep')
    def test_multiple_returns(self, mock_sleep):
        fun = Mock()
        fun.return_value = "Some random output", "Success"
        exit_code = exponential_backoff(fun, check_multiple_returns)
        mock_sleep.assert_not_called()
        self.assertEqual(exit_code, ("Some random output", "Success"))


def check_fun_test(exit_code):
    return exit_code == 0


def check_multiple_returns(returned):
    print(returned[0])
    result = returned[1]
    return result == "Success"
