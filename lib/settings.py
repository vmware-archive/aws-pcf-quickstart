import json
import re

import os

output_file = "/tmp/pcf-stack.json"


class Settings:
    def __init__(self):
        self.debug = False
        self.opsman_user = 'admin'

        with open(output_file) as output_json:
            stack_output = json.load(output_json)
            stacks = stack_output.get("Stacks")
            if not stacks:
                raise ValueError('{} should conform to {"Stacks":[{....}]}')
            self.stack = stacks[0]
            if not self.stack:
                raise ValueError('{} should conform to {"Stacks":[{....}]}')

        self.parse_environ()
        self.parse_stack()

    def parse_stack(self):
        self.stack_name = self.stack.get('StackName')
        self.stack_id = self.stack.get('StackId')
        self.key_pair_name = self.find_parameter("01NATKeyPair")
        self.pivnet_token = self.find_parameter("11PivnetToken")
        self.admin_email = self.find_parameter("12AdminEmail")
        self.elb_prefix = self.find_parameter("09ElbPrefix")

        self.ert_sql_db_password = self.find_output("PcfRdsPassword")
        self.ert_sql_db_username = self.find_output("PcfRdsUsername")
        self.pcf_iam_access_key_id = self.find_output("PcfIamUserAccessKey")
        self.pcf_iam_secret_access_key = self.find_output("PcfIamUserSecretAccessKey")
        self.vpc_id = self.find_output("PcfVpc")
        self.security_group = self.find_output("PcfVmsSecurityGroupId")
        self.zones = []
        for potential_zone in ["PcfPrivateSubnetAvailabilityZone", "PcfPrivateSubnet2AvailabilityZone"]:
            zone = self.find_output(potential_zone)
            if zone:
                self.zones.append(zone)
        self.vpc_private_subnet_id = self.find_output("PcfPrivateSubnetId")
        self.vpc_private_subnet_id2 = self.find_output("PcfPrivateSubnet2Id")
        self.vpc_private_subnet_az = self.find_output("PcfPrivateSubnetAvailabilityZone")
        self.vpc_private_subnet_az2 = self.find_output("PcfPrivateSubnet2AvailabilityZone")
        self.pcf_rds_address = self.find_output("PcfRdsAddress")
        self.pcf_rds_username = self.find_output("PcfRdsUsername")
        self.pcf_rds_password = self.find_output("PcfRdsPassword")
        self.pcf_rds_port = self.find_output("PcfRdsPort")
        self.pcf_elastic_runtime_s3_buildpacks_bucket = self.find_output("PcfElasticRuntimeS3BuildpacksBucket")
        self.pcf_elastic_runtime_s3_droplets_bucket = self.find_output("PcfElasticRuntimeS3DropletsBucket")
        self.pcf_elastic_runtime_s3_packages_bucket = self.find_output("PcfElasticRuntimeS3PackagesBucket")
        self.pcf_elastic_runtime_s3_resources_bucket = self.find_output("PcfElasticRuntimeS3ResourcesBucket")

    def parse_environ(self):
        self.dns_suffix = os.environ['DNS_SUFFIX']
        self.ops_manager_version = os.environ['OPS_MANAGER_VERSION']
        self.ert_version = os.environ['ERT_VERSION']
        self.aws_broker_version = os.environ['AWS_BROKER_VERSION']
        # use elb url, output from cloudformation template
        self.opsman_url = os.environ['OPS_MANAGER_URL']
        # todo: password charset validation?
        self.opsman_password = os.environ['OPS_MANAGER_ADMIN_PASSWORD']
        self.ssh_private_key = os.environ['SSH_PRIVATE_KEY']
        self.region = os.environ["REGION"]
        self.tile_bucket_region = os.environ['TILE_BUCKET_REGION']
        self.tile_bucket_s3_name = os.environ['TILE_BUCKET_S3_NAME']
        self.tile_bucket_s3_access_key = os.environ['TILE_BUCKET_S3_ACCESS_KEY']
        self.tile_bucket_s3_secret_access_key = os.environ['TILE_BUCKET_S3_SECRET_ACCESS_KEY']

    def get_fully_qualified_domain(self):
        return self.dns_suffix

    def find_output(self, name: str):
        for output in self.stack.get("Outputs"):
            key = output.get("OutputKey", None)
            if key == name:
                return output.get("OutputValue")
        return None

    def find_parameter(self, name: str):
        for parameter in self.stack.get("Parameters"):
            key = parameter.get("ParameterKey", None)
            if key == name:
                return parameter.get("ParameterValue")

        return None

    def get_stack_region(self):
        match = re.match(r'arn:aws:cloudformation:([-\w]*):.*', self.stack_id)
        if match is None:
            raise ValueError("StackId format does not match expecations")
        region = match.group(1)
        return region

    def get_s3_endpoint(self):
        stack_region = self.get_stack_region()
        if stack_region == "us-east-1":
            return "s3.amazonaws.com"
        else:
            return "s3-{}.amazonaws.com".format(stack_region)


def get_om_with_auth(settings: Settings):
    return "om -k --target {url} --username '{username}' --password '{password}'".format(
        url=settings.opsman_url,
        username=settings.opsman_user,
        password=settings.opsman_password
    )
