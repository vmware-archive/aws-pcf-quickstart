import boto3
import os

aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
aws_region = os.environ['AWS_INTEGRATION_REGION']

client = boto3.client(
    service_name='cloudformation', region_name=aws_region, aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

with open('../aws-pcf-concourse-state/stackid', 'r') as file:
    stackid = file.read()

client.delete_stack(StackName=stackid)
