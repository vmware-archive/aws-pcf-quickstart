import json
import os

import boto3

output_file = "/tmp/pcf-stack.json"
metadata_file = "/var/local/cloudformation/stack-meta.json"


class Settings:
    paramater_store_keys = [
        "PcfElbDnsName",
        "PcfElasticRuntimeS3BuildpacksBucket",
        "PcfIamUserAccessKey",
        "PcfIamUserSecretAccessKey",
        "PcfVpc",
        "PcfVmsSecurityGroupId",
        "PcfOpsManagerAdminPassword",
        "PcfPrivateSubnetAvailabilityZone",
        "PcfPrivateSubnet2AvailabilityZone",
        "PcfPrivateSubnetId",
        "PcfPrivateSubnet2Id",
        "PcfPrivateSubnetAvailabilityZone",
        "PcfPrivateSubnet2AvailabilityZone",
        "PcfRdsAddress",
        "PcfRdsUsername",
        "PcfRdsPassword",
        "PcfRdsPort",
        "PcfElasticRuntimeS3BuildpacksBucket",
        "PcfElasticRuntimeS3DropletsBucket",
        "PcfElasticRuntimeS3PackagesBucket",
        "PcfElasticRuntimeS3ResourcesBucket"
    ]

    def __init__(self):
        self.debug = False
        self.opsman_user = 'admin'

        self.parse_environ()
        self.parse_meta()
        self.get_parameters()
        self.describe_stack()

        self.zones = [
            self.pcf_privatesubnetavailabilityzone,
            self.pcf_privatesubnet2availabilityzone
        ]

    def parse_meta(self):
        with open(metadata_file) as meta_json:
            meta = json.load(meta_json)
            self.stack_name = meta["StackName"]
            self.stack_id = meta["StackId"]
            self.region = meta["Region"]

    @property
    def pcf_elbdnsname(self):
        return self.parameters["PcfElbDnsName"]

    @property
    def pcf_elasticruntimes3buildpacksbucket(self):
        return self.parameters["PcfElasticRuntimeS3BuildpacksBucket"]

    @property
    def pcf_iamuseraccesskey(self):
        return self.parameters["PcfIamUserAccessKey"]

    @property
    def pcf_iamusersecretaccesskey(self):
        return self.parameters["PcfIamUserSecretAccessKey"]

    @property
    def pcf_vpc(self):
        return self.parameters["PcfVpc"]

    @property
    def pcf_input_opsmanageradminpassword(self):
        return self.parameters["PcfOpsManagerAdminPassword"]

    @property
    def pcf_vmssecuritygroupid(self):
        return self.parameters["PcfVmsSecurityGroupId"]

    @property
    def pcf_privatesubnetavailabilityzone(self):
        return self.parameters["PcfPrivateSubnetAvailabilityZone"]

    @property
    def pcf_privatesubnet2availabilityzone(self):
        return self.parameters["PcfPrivateSubnet2AvailabilityZone"]

    @property
    def pcf_privatesubnetid(self):
        return self.parameters["PcfPrivateSubnetId"]

    @property
    def pcf_privatesubnet2id(self):
        return self.parameters["PcfPrivateSubnet2Id"]

    @property
    def pcf_rdsaddress(self):
        return self.parameters["PcfRdsAddress"]

    @property
    def pcf_rdsusername(self):
        return self.parameters["PcfRdsUsername"]

    @property
    def pcf_rdspassword(self):
        return self.parameters["PcfRdsPassword"]

    @property
    def pcf_rdsport(self):
        return self.parameters["PcfRdsPort"]

    @property
    def pcf_elasticruntimes3buildpacksbucket(self):
        return self.parameters["PcfElasticRuntimeS3BuildpacksBucket"]

    @property
    def pcf_elasticruntimes3dropletsbucket(self):
        return self.parameters["PcfElasticRuntimeS3DropletsBucket"]

    @property
    def pcf_elasticruntimes3packagesbucket(self):
        return self.parameters["PcfElasticRuntimeS3PackagesBucket"]

    @property
    def pcf_elasticruntimes3resourcesbucket(self):
        return self.parameters["PcfElasticRuntimeS3ResourcesBucket"]

    @property
    def pcf_input_pivnettoken(self):
        return self.input_parameters["12PivnetToken"]

    @property
    def pcf_input_pcfkeypair(self):
        return self.input_parameters["14PCFKeyPair"]

    @property
    def pcf_input_adminemail(self):
        return self.input_parameters["13AdminEmail"]

    @property
    def pcf_input_elbprefix(self):
        return self.input_parameters["10ElbPrefix"]

    @property
    def pcf_input_hostedzoneid(self):
        return self.input_parameters["14HostedZoneId"]

    @property
    def pcf_input_domain(self):
        return self.input_parameters["15Domain"]

    @property
    def pcf_input_pcfkeypairprivate(self):
        return self.input_parameters["17PCFKeyPairPrivate"]

    @property
    def opsman_url(self):
        return "https://opsman.{}".format(self.pcf_input_domain)

    def parse_environ(self):
        self.ops_manager_version = os.environ['OPS_MANAGER_VERSION']
        self.ert_version = os.environ['ERT_VERSION']
        self.aws_broker_version = os.environ['AWS_BROKER_VERSION']
        self.tile_bucket_region = os.environ['TILE_BUCKET_REGION']
        self.tile_bucket_s3_name = os.environ['TILE_BUCKET_S3_NAME']

    def get_s3_endpoint(self):
        stack_region = self.region
        if stack_region == "us-east-1":
            return "s3.amazonaws.com"
        else:
            return "s3-{}.amazonaws.com".format(stack_region)

    def get_parameters(self):
        self.parameters = {}
        client = boto3.client(
            service_name='ssm', region_name=self.region
        )
        parameters = self.paramater_store_keys
        parameter_names = ["{}.{}".format(self.stack_name, p) for p in parameters]
        for parameter_name_set in chunk(parameter_names, 10):
            response = client.get_parameters(
                Names=parameter_name_set,
                WithDecryption=False
            )

            param_results = response.get("Parameters")
            for result in param_results:
                prefix = self.stack_name + "."
                name = result['Name'].replace(prefix, "", 1)
                self.parameters[name] = result['Value']

    def describe_stack(self):
        self.input_parameters = {}
        client = boto3.client(
            service_name='cloudformation', region_name=self.region
        )
        response = client.describe_stacks(StackName=self.stack_id)
        param_results = response['Stacks'][0].get("Parameters")

        for result in param_results:
            self.input_parameters[result.get('ParameterKey')] = result['ParameterValue']


def chunk(l, n):
    return list(__chunk_generator(l, n))


def __chunk_generator(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def get_om_with_auth(settings: Settings):
    return "om -k --target {url} --username '{username}' --password '{password}'".format(
        url=settings.opsman_url,
        username=settings.opsman_user,
        password=settings.pcf_input_opsmanageradminpassword
    )
