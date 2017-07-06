import json
import unittest

from mock import Mock, patch

import delete_check
from settings import Settings


class TestDeleteCheck(unittest.TestCase):
    def setUp(self):
        self.settings = Mock(Settings)
        self.settings.region = 'canada-1a'
        self.settings.pcf_pcfcustomresourcesqsqueueurl = 'https://queue.example.com'
        self.settings.debug = False

        self.response = {'Messages':
            [
                {
                    'Body': '{\n  "Type" : "Notification",\n  "MessageId" : "3c71d3a0-7d25-59b1-93bc-8213196855a7",\n  "TopicArn" : "arn:aws:sns:us-west-2:540420658117:custom-resource-maybe-4-SNSTopic-11NVYUIXWZTXZ",\n  "Subject" : "AWS CloudFormation custom resource request",\n  "Message" : "{\\"RequestType\\":\\"Delete\\",\\"ServiceToken\\":\\"arn:aws:sns:us-west-2:540420658117:custom-resource-maybe-4-SNSTopic-11NVYUIXWZTXZ\\",\\"ResponseURL\\":\\"https://cloudformation-custom-resource-response-uswest2.s3-us-west-2.amazonaws.com/arn%3Aaws%3Acloudformation%3Aus-west-2%3A530420658117%3Astack/pcf-stack/1e820540-4c58-11e7-a965-50d5ca0184f2%7CMyCustomResource%7C4dd2c9a0-04cb-4218-908c-e3cdfad3c634?AWSAccessKeyId=AKIAI4KYMPPRGQACET5Q&Expires=1496940077&Signature=uLbeSl3rtkuDa2xf0y9oMFc1zBI%3D\\",\\"StackId\\":\\"arn:aws:cloudformation:us-west-2:540420658117:stack/pcf-stack/1e820540-4c58-11e7-a965-50d5ca0184f2\\",\\"RequestId\\":\\"4dd2c9a0-04cb-4218-908c-e2cdfad3c634\\",\\"LogicalResourceId\\":\\"MyCustomResource\\",\\"ResourceType\\":\\"Custom::CloudFoundryPhase1\\",\\"ResourceProperties\\":{\\"ServiceToken\\":\\"arn:aws:sns:us-west-2:540410658117:custom-resource-maybe-4-SNSTopic-11NVZUIXWZTXZ\\",\\"ExampleProperty2\\":\\"ExampleValue2\\",\\"ExampleProperty1\\":\\"ExampleValue1\\"}}",\n  "Timestamp" : "2017-06-08T14:41:17.469Z",\n  "SignatureVersion" : "1",\n  "Signature" : "eNbpNJ+mzhH4qRP89tIWj96cK0nCirmNkwjQe/3DAgWnuhKKYKvtkffZu04uTynb/Tjt/5O7y/dfUy5cTmauhAx9g8gFkwH4vQVGhJOgEI6hFEHqRgY+8FwfeKowDiZTJyixwuqY9O1wqXxOb9q0rsLpApZCVwHsIhXio3ATdmJVNuJZhpC+0Dae1jnAg7nRyLAOrjEI8yaGLLoA1s/KdrZakclwGIgNj+/as4Vscbd1+VH59cpzryoHpOIjQrESTsCqCSSHh9H4j10wjDAeFxDY3lAZOZu+SlWOsCshv+4xRiJMmWY+WCgJ2UuAXnj7N6QPKwXwnPV1UmdkXGaGWQ==",\n  "SigningCertURL" : "https://sns.us-west-2.amazonaws.com/SimpleNotificationService-b95095beb82e8q6a046b3aafc7f4149a.pem",\n  "UnsubscribeURL" : "https://sns.us-west-2.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-west-2:540420258117:custom-resource-maybe-4-SNSTopic-11NVYUIXWZTXZ:dc93952d-b252-4da3-a726-7df99631df02"\n}',
                    'MD5OfBody': '46e9054484367800fbd6bb8e13aaea36',
                    'MessageId': '6eef8c02-9874-41f8-8883-9788b911b773',
                    'ReceiptHandle': 'AQEBCLcjvnWL65ILiE9/L6WzthEatj3punqXWcxK/VGSfOhkjbfaMoy6GHtxPr/giOjO2gIW7buTv9Mkhk7/tpgbgJEm338nzoLOxqiW4s3fzoQWrjDu0HHpcD1KrMJBeVstxnLglEOOny2KRozfsLjbeH5HoXuo+8mrb0nwVUglIK2vBkAPHLOGu64/BPOR6dt2qgYK4hzytgXQprcLlS5rYrrpYkqBKjWt9PCuwSG244LuN3brNyRIgxPR9SQ/ja9CWocx7sS3Ri6tAVU8zP4OxjRmfdMj/EEdL3Wm5m4v7+hnGDnj0LSV/3UX6C1/ozIOtHY6bqN6HQ6nM48Dk6UTEm78ApFuYmOFnh5xfcAEJHHN9meqnMsYMe0l8hTEBRHDYII/W4K5APbUNNsuoU/R3uYgqWlNMFWDvxSORKPwy/2O0Kk51+ZE/fyGEaVncoof'
                },
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

    @patch('sqs.get_messages')
    @patch('delete_everything.delete_everything')
    @patch('sqs.report_cr_deletion_success')
    def test_check(self, mock_report_deletion_success, mock_delete_everything, mock_get_messages):
        mock_get_messages.return_value = self.response.get('Messages')
        mock_delete_everything.return_value = "", "", 0

        delete_check.check(self.settings)

        mock_delete_everything.assert_called()
        mock_report_deletion_success.assert_called()

    @patch('sqs.get_messages')
    @patch('delete_everything.delete_everything')
    @patch('sqs.report_cr_deletion_failure')
    def test_check_delete_everything_failure(self, mock_report_deletion_failure, mock_delete_everything,
                                             mock_get_messages):
        mock_get_messages.return_value = self.response.get('Messages')
        mock_delete_everything.return_value = "Fail", "", 1

        delete_check.check(self.settings)

        mock_delete_everything.assert_called()
        mock_report_deletion_failure.assert_called()

    @patch('sqs.get_messages')
    @patch('delete_everything.delete_everything')
    @patch('sqs.report_cr_deletion_failure')
    def test_skips_deletion_when_no_message(self, mock_report_deletion_failure, mock_delete_everything,
                                            mock_get_messages):
        messages = [
            {
                'Body': '{\n  "Type" : "Notification",\n  "MessageId" : "3c71d3a0-7d25-59b1-93bc-8213196855a7",\n  "TopicArn" : "arn:aws:sns:us-west-2:540420658117:custom-resource-maybe-4-SNSTopic-11NVYUIXWZTXZ",\n  "Subject" : "AWS CloudFormation custom resource request",\n  "Message" : "{\\"RequestType\\":\\"Create\\",\\"ServiceToken\\":\\"arn:aws:sns:us-west-2:540420658117:custom-resource-maybe-4-SNSTopic-11NVYUIXWZTXZ\\",\\"ResponseURL\\":\\"https://cloudformation-custom-resource-response-uswest2.s3-us-west-2.amazonaws.com/arn%3Aaws%3Acloudformation%3Aus-west-2%3A530420658117%3Astack/pcf-stack/1e820540-4c58-11e7-a965-50d5ca0184f2%7CMyCustomResource%7C4dd2c9a0-04cb-4218-908c-e3cdfad3c634?AWSAccessKeyId=AKIAI4KYMPPRGQACET5Q&Expires=1496940077&Signature=uLbeSl3rtkuDa2xf0y9oMFc1zBI%3D\\",\\"StackId\\":\\"arn:aws:cloudformation:us-west-2:540420658117:stack/pcf-stack/1e820540-4c58-11e7-a965-50d5ca0184f2\\",\\"RequestId\\":\\"4dd2c9a0-04cb-4218-908c-e2cdfad3c634\\",\\"LogicalResourceId\\":\\"MyCustomResource\\",\\"ResourceType\\":\\"Custom::CloudFoundryPhase1\\",\\"ResourceProperties\\":{\\"ServiceToken\\":\\"arn:aws:sns:us-west-2:540410658117:custom-resource-maybe-4-SNSTopic-11NVZUIXWZTXZ\\",\\"ExampleProperty2\\":\\"ExampleValue2\\",\\"ExampleProperty1\\":\\"ExampleValue1\\"}}",\n  "Timestamp" : "2017-06-08T14:41:17.469Z",\n  "SignatureVersion" : "1",\n  "Signature" : "eNbpNJ+mzhH4qRP89tIWj96cK0nCirmNkwjQe/3DAgWnuhKKYKvtkffZu04uTynb/Tjt/5O7y/dfUy5cTmauhAx9g8gFkwH4vQVGhJOgEI6hFEHqRgY+8FwfeKowDiZTJyixwuqY9O1wqXxOb9q0rsLpApZCVwHsIhXio3ATdmJVNuJZhpC+0Dae1jnAg7nRyLAOrjEI8yaGLLoA1s/KdrZakclwGIgNj+/as4Vscbd1+VH59cpzryoHpOIjQrESTsCqCSSHh9H4j10wjDAeFxDY3lAZOZu+SlWOsCshv+4xRiJMmWY+WCgJ2UuAXnj7N6QPKwXwnPV1UmdkXGaGWQ==",\n  "SigningCertURL" : "https://sns.us-west-2.amazonaws.com/SimpleNotificationService-b95095beb82e8q6a046b3aafc7f4149a.pem",\n  "UnsubscribeURL" : "https://sns.us-west-2.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-west-2:540420258117:custom-resource-maybe-4-SNSTopic-11NVYUIXWZTXZ:dc93952d-b252-4da3-a726-7df99631df02"\n}',
                'MD5OfBody': '46e9054484367800fbd6bb8e13aaea36',
                'MessageId': '6eef8c02-9874-41f8-8883-9788b911b773',
                'ReceiptHandle': 'AQEBCLcjvnWL65ILiE9/L6WzthEatj3punqXWcxK/VGSfOhkjbfaMoy6GHtxPr/giOjO2gIW7buTv9Mkhk7/tpgbgJEm338nzoLOxqiW4s3fzoQWrjDu0HHpcD1KrMJBeVstxnLglEOOny2KRozfsLjbeH5HoXuo+8mrb0nwVUglIK2vBkAPHLOGu64/BPOR6dt2qgYK4hzytgXQprcLlS5rYrrpYkqBKjWt9PCuwSG244LuN3brNyRIgxPR9SQ/ja9CWocx7sS3Ri6tAVU8zP4OxjRmfdMj/EEdL3Wm5m4v7+hnGDnj0LSV/3UX6C1/ozIOtHY6bqN6HQ6nM48Dk6UTEm78ApFuYmOFnh5xfcAEJHHN9meqnMsYMe0l8hTEBRHDYII/W4K5APbUNNsuoU/R3uYgqWlNMFWDvxSORKPwy/2O0Kk51+ZE/fyGEaVncoof'
            },
            {
                'Body': '{\n  "Type" : "Notification",\n  "MessageId" : "3c71d3a0-7d25-59b1-93bc-8213196855a7",\n  "TopicArn" : "arn:aws:sns:us-west-2:540420658117:custom-resource-maybe-4-SNSTopic-11NVYUIXWZTXZ",\n  "Subject" : "AWS CloudFormation custom resource request",\n  "Message" : "{\\"RequestType\\":\\"Create\\",\\"ServiceToken\\":\\"arn:aws:sns:us-west-2:540420658117:custom-resource-maybe-4-SNSTopic-11NVYUIXWZTXZ\\",\\"ResponseURL\\":\\"https://cloudformation-custom-resource-response-uswest2.s3-us-west-2.amazonaws.com/arn%3Aaws%3Acloudformation%3Aus-west-2%3A530420658117%3Astack/pcf-stack/1e820540-4c58-11e7-a965-50d5ca0184f2%7CMyCustomResource%7C4dd2c9a0-04cb-4218-908c-e3cdfad3c634?AWSAccessKeyId=AKIAI4KYMPPRGQACET5Q&Expires=1496940077&Signature=uLbeSl3rtkuDa2xf0y9oMFc1zBI%3D\\",\\"StackId\\":\\"arn:aws:cloudformation:us-west-2:540420658117:stack/pcf-stack/1e820540-4c58-11e7-a965-50d5ca0184f2\\",\\"RequestId\\":\\"4dd2c9a0-04cb-4218-908c-e2cdfad3c634\\",\\"LogicalResourceId\\":\\"MyCustomResource\\",\\"ResourceType\\":\\"Custom::CloudFoundryPhase1\\",\\"ResourceProperties\\":{\\"ServiceToken\\":\\"arn:aws:sns:us-west-2:540410658117:custom-resource-maybe-4-SNSTopic-11NVZUIXWZTXZ\\",\\"ExampleProperty2\\":\\"ExampleValue2\\",\\"ExampleProperty1\\":\\"ExampleValue1\\"}}",\n  "Timestamp" : "2017-06-08T14:41:17.469Z",\n  "SignatureVersion" : "1",\n  "Signature" : "eNbpNJ+mzhH4qRP89tIWj96cK0nCirmNkwjQe/3DAgWnuhKKYKvtkffZu04uTynb/Tjt/5O7y/dfUy5cTmauhAx9g8gFkwH4vQVGhJOgEI6hFEHqRgY+8FwfeKowDiZTJyixwuqY9O1wqXxOb9q0rsLpApZCVwHsIhXio3ATdmJVNuJZhpC+0Dae1jnAg7nRyLAOrjEI8yaGLLoA1s/KdrZakclwGIgNj+/as4Vscbd1+VH59cpzryoHpOIjQrESTsCqCSSHh9H4j10wjDAeFxDY3lAZOZu+SlWOsCshv+4xRiJMmWY+WCgJ2UuAXnj7N6QPKwXwnPV1UmdkXGaGWQ==",\n  "SigningCertURL" : "https://sns.us-west-2.amazonaws.com/SimpleNotificationService-b95095beb82e8q6a046b3aafc7f4149a.pem",\n  "UnsubscribeURL" : "https://sns.us-west-2.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-west-2:540420258117:custom-resource-maybe-4-SNSTopic-11NVYUIXWZTXZ:dc93952d-b252-4da3-a726-7df99631df02"\n}',
                'MD5OfBody': '46e9054484367800fbd6bb8e13aaea36',
                'MessageId': '6eef8c02-9874-41f8-8883-9788b911b773',
                'ReceiptHandle': 'AQEBCLcjvnWL65ILiE9/L6WzthEatj3punqXWcxK/VGSfOhkjbfaMoy6GHtxPr/giOjO2gIW7buTv9Mkhk7/tpgbgJEm338nzoLOxqiW4s3fzoQWrjDu0HHpcD1KrMJBeVstxnLglEOOny2KRozfsLjbeH5HoXuo+8mrb0nwVUglIK2vBkAPHLOGu64/BPOR6dt2qgYK4hzytgXQprcLlS5rYrrpYkqBKjWt9PCuwSG244LuN3brNyRIgxPR9SQ/ja9CWocx7sS3Ri6tAVU8zP4OxjRmfdMj/EEdL3Wm5m4v7+hnGDnj0LSV/3UX6C1/ozIOtHY6bqN6HQ6nM48Dk6UTEm78ApFuYmOFnh5xfcAEJHHN9meqnMsYMe0l8hTEBRHDYII/W4K5APbUNNsuoU/R3uYgqWlNMFWDvxSORKPwy/2O0Kk51+ZE/fyGEaVncoof'
            }
        ]

        mock_get_messages.return_value = messages

        delete_check.check(self.settings)

        mock_delete_everything.assert_not_called()
