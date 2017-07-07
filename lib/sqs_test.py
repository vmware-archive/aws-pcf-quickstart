import json
import unittest

from mock import Mock, patch

import sqs
from settings import Settings


class TestSqs(unittest.TestCase):
    def setUp(self):
        self.settings = Mock(Settings)
        self.settings.region = 'canada-1a'
        self.settings.pcf_pcfcustomresourcesqsqueueurl = 'https://queue.example.com'
        self.settings.debug = False

        self.response = {'Messages':
            [
                {
                    'Body': '{\n  "Type" : "Notification",\n  "MessageId" : "3c71d3a0-7d25-59b1-93bc-8213196855a7",\n  "TopicArn" : "arn:aws:sns:us-west-2:540420658117:custom-resource-maybe-4-SNSTopic-11NVYUIXWZTXZ",\n  "Subject" : "AWS CloudFormation custom resource request",\n  "Message" : "{\\"RequestType\\":\\"Create\\",\\"ServiceToken\\":\\"arn:aws:sns:us-west-2:540420658117:custom-resource-maybe-4-SNSTopic-11NVYUIXWZTXZ\\",\\"ResponseURL\\":\\"https://cloudformation-custom-resource-response-uswest2.s3-us-west-2.amazonaws.com/arn%3Aaws%3Acloudformation%3Aus-west-2%3A530420658117%3Astack/pcf-stack/1e820540-4c58-11e7-a965-50d5ca0184f2%7CMyCustomResource%7C4dd2c9a0-04cb-4218-908c-e3cdfad3c634?AWSAccessKeyId=AKIAI4KYMPPRGQACET5Q&Expires=1496940077&Signature=uLbeSl3rtkuDa2xf0y9oMFc1zBI%3D\\",\\"StackId\\":\\"arn:aws:cloudformation:us-west-2:540420658117:stack/pcf-stack/1e820540-4c58-11e7-a965-50d5ca0184f2\\",\\"RequestId\\":\\"4dd2c9a0-04cb-4218-908c-e2cdfad3c634\\",\\"LogicalResourceId\\":\\"MyCustomResource\\",\\"ResourceType\\":\\"Custom::CloudFoundryPhase1\\",\\"ResourceProperties\\":{\\"ServiceToken\\":\\"arn:aws:sns:us-west-2:540410658117:custom-resource-maybe-4-SNSTopic-11NVZUIXWZTXZ\\",\\"ExampleProperty2\\":\\"ExampleValue2\\",\\"ExampleProperty1\\":\\"ExampleValue1\\"}}",\n  "Timestamp" : "2017-06-08T14:41:17.469Z",\n  "SignatureVersion" : "1",\n  "Signature" : "eNbpNJ+mzhH4qRP89tIWj96cK0nCirmNkwjQe/3DAgWnuhKKYKvtkffZu04uTynb/Tjt/5O7y/dfUy5cTmauhAx9g8gFkwH4vQVGhJOgEI6hFEHqRgY+8FwfeKowDiZTJyixwuqY9O1wqXxOb9q0rsLpApZCVwHsIhXio3ATdmJVNuJZhpC+0Dae1jnAg7nRyLAOrjEI8yaGLLoA1s/KdrZakclwGIgNj+/as4Vscbd1+VH59cpzryoHpOIjQrESTsCqCSSHh9H4j10wjDAeFxDY3lAZOZu+SlWOsCshv+4xRiJMmWY+WCgJ2UuAXnj7N6QPKwXwnPV1UmdkXGaGWQ==",\n  "SigningCertURL" : "https://sns.us-west-2.amazonaws.com/SimpleNotificationService-b95095beb82e8q6a046b3aafc7f4149a.pem",\n  "UnsubscribeURL" : "https://sns.us-west-2.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-west-2:540420258117:custom-resource-maybe-4-SNSTopic-11NVYUIXWZTXZ:dc93952d-b252-4da3-a726-7df99631df02"\n}',
                    'MD5OfBody': '46e9054484367800fbd6bb8e13aaea36',
                    'MessageId': '6eef8c02-9874-41f8-8883-9788b911b773',
                    'ReceiptHandle': 'AQEBCLcjvnWL65ILiE9/L6WzthEatj3punqXWcxK/VGSfOhkjbfaMoy6GHtxPr/giOjO2gIW7buTv9Mkhk7/tpgbgJEm338nzoLOxqiW4s3fzoQWrjDu0HHpcD1KrMJBeVstxnLglEOOny2KRozfsLjbeH5HoXuo+8mrb0nwVUglIK2vBkAPHLOGu64/BPOR6dt2qgYK4hzytgXQprcLlS5rYrrpYkqBKjWt9PCuwSG244LuN3brNyRIgxPR9SQ/ja9CWocx7sS3Ri6tAVU8zP4OxjRmfdMj/EEdL3Wm5m4v7+hnGDnj0LSV/3UX6C1/ozIOtHY6bqN6HQ6nM48Dk6UTEm78ApFuYmOFnh5xfcAEJHHN9meqnMsYMe0l8hTEBRHDYII/W4K5APbUNNsuoU/R3uYgqWlNMFWDvxSORKPwy/2O0Kk51+ZE/fyGEaVncoof'
                }
            ],
            'ResponseMetadata': {
                'HTTPStatusCode': 200, 'HTTPHeaders': {
                    'connection': 'keep-alive', 'server': 'Server',
                    'content-length': '3342',
                    'content-type': 'text/xml',
                    'date': 'Thu, 08 Jun 2017 15:20:07 GMT',
                    'x-amzn-requestid': '116092e7-fee7-5580-b276-c3549380b837'
                },
                'RequestId': '116092e7-fee7-5580-b276-c3549380b837', 'RetryAttempts': 0
            }
        }

    @patch('boto3.client')
    def test_get_messages(self, mock_client_constructor):
        mock_client = Mock()
        mock_client_constructor.return_value = mock_client
        mock_client.receive_message.return_value = self.response

        messages = sqs.get_messages(self.settings)

        mock_client_constructor.assert_called_with(
            service_name="sqs",
            region_name="canada-1a"
        )
        mock_client.receive_message.assert_called_with(
            QueueUrl="https://queue.example.com",
            MaxNumberOfMessages=10,
            VisibilityTimeout=1
        )

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].get('MD5OfBody'), '46e9054484367800fbd6bb8e13aaea36')

    @patch('sqs.delete_messages')
    @patch('sqs.get_messages')
    @patch('requests.put')
    def test_report_status(self, mock_put, mock_get_messages, mock_delete_messages):
        mock_get_messages.return_value = self.response.get('Messages')

        return_code = sqs.report_status(self.settings, 'Create', '', 'MyCustomResource', 'SUCCESS')

        expected_body = {
            'Status': 'SUCCESS',
            'PhysicalResourceId': 'PivotalCloudFoundry',
            'RequestId': '4dd2c9a0-04cb-4218-908c-e2cdfad3c634',
            'Reason': '',
            'LogicalResourceId': 'MyCustomResource',
            'StackId': 'arn:aws:cloudformation:us-west-2:540420658117:stack/pcf-stack/1e820540-4c58-11e7-a965-50d5ca0184f2',
            'Data': {}
        }

        self.assertEqual(mock_put.call_count, 1)
        call_args = mock_put.call_args[1]
        self.assertEqual(
            call_args.get('url'),
            'https://cloudformation-custom-resource-response-uswest2.s3-us-west-2.amazonaws.com/arn%3Aaws%3Acloudformation%3Aus-west-2%3A530420658117%3Astack/pcf-stack/1e820540-4c58-11e7-a965-50d5ca0184f2%7CMyCustomResource%7C4dd2c9a0-04cb-4218-908c-e3cdfad3c634'
        )
        self.assertEqual(
            call_args.get('params'),
            'AWSAccessKeyId=AKIAI4KYMPPRGQACET5Q&Expires=1496940077&Signature=uLbeSl3rtkuDa2xf0y9oMFc1zBI%3D'
        )
        self.assertEqual(json.loads(call_args.get('data').decode('utf-8')), expected_body)
        self.assertEqual(return_code, 0)
        self.assertEqual(mock_delete_messages.call_count, 1)

    @patch('sqs.get_messages')
    @patch('requests.put')
    def test_report_status_no_messages(self, mock_put, mock_get_messages):
        mock_get_messages.return_value = []

        return_code = sqs.report_status(self.settings, '', '', 'MyCustomResource', 'SUCCESS')

        self.assertEqual(return_code, 1)
        mock_put.assert_not_called()

    @patch('boto3.client')
    def test_delete_message(self, mock_client_constructor):
        mock_client = Mock()
        mock_client_constructor.return_value = mock_client
        mock_client.delete_message.return_value = self.response

        message = self.response.get('Messages')[0]

        sqs.delete_messages(self.settings, message)

        self.assertEqual(mock_client.delete_message.call_count, 1)
        mock_client.delete_message.assert_called_with(
            QueueUrl="https://queue.example.com",
            ReceiptHandle="AQEBCLcjvnWL65ILiE9/L6WzthEatj3punqXWcxK/VGSfOhkjbfaMoy6GHtxPr/giOjO2gIW7buTv9Mkhk7/tpgbgJEm338nzoLOxqiW4s3fzoQWrjDu0HHpcD1KrMJBeVstxnLglEOOny2KRozfsLjbeH5HoXuo+8mrb0nwVUglIK2vBkAPHLOGu64/BPOR6dt2qgYK4hzytgXQprcLlS5rYrrpYkqBKjWt9PCuwSG244LuN3brNyRIgxPR9SQ/ja9CWocx7sS3Ri6tAVU8zP4OxjRmfdMj/EEdL3Wm5m4v7+hnGDnj0LSV/3UX6C1/ozIOtHY6bqN6HQ6nM48Dk6UTEm78ApFuYmOFnh5xfcAEJHHN9meqnMsYMe0l8hTEBRHDYII/W4K5APbUNNsuoU/R3uYgqWlNMFWDvxSORKPwy/2O0Kk51+ZE/fyGEaVncoof"
        )

    @patch('util.exponential_backoff')
    @patch('sqs.report_status')
    def test_report_status_backoff(self, mock_report_status, mock_backoff):
        sqs.report_cr_creation_success(self.settings, '', 'MyCustomResource')

        mock_backoff.assert_called()

        mock_backoff.call_args[0][0]()
        mock_report_status.assert_called_with(
            self.settings, 'Create', '', 'MyCustomResource', 'SUCCESS'
        )

    @patch('sqs.report_status_backoff')
    def test_report_creation_success(self, mock_report_status_backoff):
        sqs.report_cr_creation_success(self.settings, '', 'MyCustomResource')

        mock_report_status_backoff.assert_called_with(
            self.settings, 'Create', '', 'MyCustomResource', 'SUCCESS'
        )

    @patch('sqs.report_status_backoff')
    def test_report_creation_failure(self, mock_report_status_backoff):
        sqs.report_cr_creation_failure(self.settings, '', 'MyCustomResource')

        mock_report_status_backoff.assert_called_with(
            self.settings, 'Create', '', 'MyCustomResource', 'FAILED'
        )

    @patch('sqs.report_status_backoff')
    def test_report_creation_success(self, mock_report_status_backoff):
        sqs.report_cr_creation_success(self.settings, '', 'MyCustomResource')

        mock_report_status_backoff.assert_called_with(
            self.settings, 'Delete', '', 'MyCustomResource', 'SUCCESS'
        )

    @patch('sqs.report_status_backoff')
    def test_report_creation_success(self, mock_report_status_backoff):
        sqs.report_cr_deletion_failure(self.settings, '', 'MyCustomResource')

        mock_report_status_backoff.assert_called_with(
            self.settings, 'Delete', '', 'MyCustomResource', 'FAILED'
        )
