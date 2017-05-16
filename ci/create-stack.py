import boto3
import datetime
import time
import sys
import os


def describe_stack_status(cloudformation_client, stack_id):
    describe_response = cloudformation_client.describe_stacks(StackName=stack_id)
    stack = describe_response.get("Stacks")[0]

    return stack.get('StackStatus')


password = os.environ['AWS_CF_PASSWORD']
domain = os.environ['AWS_CF_DOMAIN']
hostedzoneid = os.environ['AWS_CF_HOSTEDZONEID']
sslcertificatearn = os.environ['AWS_CF_SSLCERTIFICATEARN']
natkeypair = os.environ['AWS_CF_NATKEYPAIR']
pivnettoken = os.environ['AWS_CF_PIVNETTOKEN']
aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
aws_region = os.environ['AWS_INTEGRATION_REGION']

parameters = [
    {"ParameterKey": "06RdsPassword", "ParameterValue": password},
    {"ParameterKey": "14HostedZoneId", "ParameterValue": hostedzoneid},
    {"ParameterKey": "01NATKeyPair", "ParameterValue": natkeypair},
    {"ParameterKey": "07SSLCertificateARN", "ParameterValue": sslcertificatearn},
    {"ParameterKey": "16OpsManagerAdminPassword", "ParameterValue": password},
    {"ParameterKey": "15Domain", "ParameterValue": domain},
    {"ParameterKey": "10ElbPrefix", "ParameterValue": "my-pcf-elb"},
    {"ParameterKey": "14PCFKeyPair", "ParameterValue": natkeypair},
    {"ParameterKey": "05RdsUsername", "ParameterValue": "admin"},
    {"ParameterKey": "13AdminEmail", "ParameterValue": "noreply@pivotal.io"},
    {"ParameterKey": "12PivnetToken", "ParameterValue": pivnettoken}
]

client = boto3.client(
    service_name='cloudformation', region_name=aws_region, aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

with open('./cloudformation/quickstart-template.yml', 'r') as template_file:
    template = template_file.read()

    stack_name = "pcf-int-{}".format(int(datetime.datetime.now().timestamp()))
    create_response = client.create_stack(
        StackName=stack_name,
        TemplateBody=template,
        Parameters=parameters,
        Capabilities=[
            'CAPABILITY_IAM',
        ],
    )
    stack_id = create_response.get("StackId")
    print("Created stack: {}".format(stack_id))

    stack_status = describe_stack_status(client, stack_id)
    while stack_status == 'CREATE_IN_PROGRESS':
        time.sleep(300)
        stack_status = describe_stack_status(client, stack_id)
        print("Checking status got {}".format(stack_status))

    print("Final status {}".format(stack_status))
    if stack_status != "CREATE_COMPLETE":
        print("Stack creation did not complete, exiting...")
        sys.exit(1)
    else:
        sys.exit(0)
