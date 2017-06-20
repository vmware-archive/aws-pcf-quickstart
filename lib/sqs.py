import json

import boto3
import requests

import settings


def report_cr_creation_failure(my_settings: settings.Settings, logical_resource_id: str):
    return report_create_status(my_settings, logical_resource_id, 'FAILED')


def report_cr_creation_success(my_settings: settings.Settings, logical_resource_id: str):
    return report_create_status(my_settings, logical_resource_id, 'SUCCESS')


def report_create_status(my_settings: settings.Settings, logical_resource_id: str, status: str):
    raw_message = get_messages(my_settings)
    if len(raw_message) < 1:
        print("No message on queue... so we can't report back")
        return 1
    messages = [parse_message(m) for m in raw_message]
    create_messages = [
        m for m in messages if
        m.get('RequestType') == 'Create' and m.get('LogicalResourceId') == logical_resource_id
    ]
    if len(create_messages) < 1:
        print("No message of type 'Create', so unable to report back to CloudFormation")
        return 1
    create_message = create_messages[0]
    response_for_cloud_formation = build_payload(create_message, status)

    response_url_full = create_message.get('ResponseURL')
    print('Uploading to signed url: {}'.format(response_url_full))
    response_url, response_params = response_url_full.split('?')
    requests.put(
        url=response_url,
        params=response_params,
        data=str.encode(json.dumps(response_for_cloud_formation))
    )

    for create_message in create_messages:
        print("Deleting message", create_message.get('ReceiptHandle'))
        delete_messages(my_settings, create_message)

    return 0


def build_payload(create_message, status):
    return {
        'Status': status,
        'PhysicalResourceId': 'PivotalCloudFoundry',
        'RequestId': create_message.get('RequestId'),
        'LogicalResourceId': create_message.get('LogicalResourceId'),
        'StackId': create_message.get('StackId'),
        'Data': {}
    }


def parse_message(matryoshka_message):
    body = json.loads(matryoshka_message.get('Body'))
    print("Parsed message, body")
    print(body)
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
    # todo: remove debugging
    print("-------------------------")
    print(json.dumps(response, indent="  "))
    print("-------------------------")

    return response.get('Messages', [])
