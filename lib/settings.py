import os
import json

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
        self.key_pair_name = self.find_parameter("01NATKeyPair")
        self.pivnet_token = self.find_parameter("11PivnetToken")

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


    def parse_environ(self):
        self.dns_suffix = os.environ['DNS_SUFFIX']
        self.ops_manager_version = os.environ['OPS_MANAGER_VERSION']
        # use elb url, output from cloudformation template
        self.opsman_url = os.environ['OPS_MANAGER_URL']
        # todo: password charset validation?
        self.opsman_password = os.environ['OPS_MANAGER_ADMIN_PASSWORD']
        self.ssh_private_key = os.environ['SSH_PRIVATE_KEY']
        self.region = os.environ["REGION"]


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


def get_om_with_auth(settings: Settings):
    return "om -k --target {url} --username '{username}' --password '{password}'".format(
        url=settings.opsman_url,
        username=settings.opsman_user,
        password=settings.opsman_password
    )
