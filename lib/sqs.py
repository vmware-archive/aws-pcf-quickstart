import functools
import json

import boto3
import requests

import settings
import util


def check_report_status(return_code):
    return return_code == 0


def report_cr_creation_success(my_settings: settings.Settings, reason: str, logical_res_id: str = ""):
    return report_status_backoff(my_settings, 'Create', reason, logical_res_id, 'SUCCESS')


def report_cr_creation_failure(my_settings: settings.Settings, reason: str, logical_res_id: str = ""):
    return report_status_backoff(my_settings, 'Create', reason, logical_res_id, 'FAILED')


def report_cr_deletion_success(my_settings: settings.Settings, reason: str, logical_res_id: str = ""):
    return report_status_backoff(my_settings, 'Delete', reason, logical_res_id, 'SUCCESS')


def report_cr_deletion_failure(my_settings: settings.Settings, reason: str, logical_res_id: str = ""):
    return report_status_backoff(my_settings, 'Delete', reason, logical_res_id, 'FAILED')


def report_status_backoff(my_settings: settings.Settings, req_type: str, reason: str, logical_res_id: str, status: str):
    return util.exponential_backoff(
        functools.partial(report_status, my_settings, req_type, reason, logical_res_id, 'SUCCESS'),
        check_report_status
    )


def report_status(my_settings: settings.Settings, req_type: str, reason: str, logical_res_id: str, status: str):
    raw_message = get_messages(my_settings)
    if len(raw_message) < 1:
        print("No message on queue... so we can't report back")
        return 1
    messages = [parse_message(m) for m in raw_message]
    filtered_messages = [m for m in messages if m.get('RequestType') == req_type]
    if logical_res_id != "":
        filtered_messages = [m for m in messages if m.get('LogicalResourceId') == logical_res_id]

    if len(filtered_messages) < 1:
        print("No message of type '{}', so unable to report back to CloudFormation".format(req_type))
        return 1

    for message in filtered_messages:
        response_for_cloud_formation = build_payload(message, status, reason)
        response_url_full = message.get('ResponseURL')
        response_url, response_params = response_url_full.split('?')
        requests.put(
            url=response_url, params=response_params,
            data=str.encode(json.dumps(response_for_cloud_formation))
        )

        print("Deleting message", message.get('ReceiptHandle'))
        delete_messages(my_settings, message)

    return 0


def build_payload(create_message, status: str, reason: str):
    return {
        'Status': status,
        'Reason': reason,
        'PhysicalResourceId': 'PivotalCloudFoundry',
        'RequestId': create_message.get('RequestId'),
        'LogicalResourceId': create_message.get('LogicalResourceId'),
        'StackId': create_message.get('StackId'),
        'Data': {}
    }


def parse_message(matryoshka_message):
    body = json.loads(matryoshka_message.get('Body'))
    parsed = json.loads(body.get('Message'))
    parsed["ReceiptHandle"] = matryoshka_message.get("ReceiptHandle")

    return parsed


def delete_messages(my_settings: settings.Settings, message):
    sqs = boto3.client(service_name='sqs', region_name=my_settings.region)
    sqs.delete_message(
        QueueUrl=my_settings.pcf_pcfcustomresourcesqsqueueurl,
        ReceiptHandle=message.get('ReceiptHandle')
    )


def get_messages(my_settings: settings.Settings):
    sqs = boto3.client(service_name='sqs', region_name=my_settings.region)
    response = sqs.receive_message(
        QueueUrl=my_settings.pcf_pcfcustomresourcesqsqueueurl,
        MaxNumberOfMessages=10,
        VisibilityTimeout=1
    )
    print("SQS Messages")
    print(json.dumps(response, indent="  "))

    return response.get('Messages', [])
