import json
import os

import boto3

output_file = "/tmp/pcf-stack.json"
metadata_file = "/var/local/cloudformation/stack-meta.json"

ops_manager_version = "1.10.4"
ert_version = "1.10.4-build.1"
aws_broker_version = "1.2.0.147"
tile_bucket_s3_name = "pcf-quickstart-tiles"
tile_bucket_region = "us-west-2"


class Settings:
    paramater_store_keys = [
        "PcfElbDnsName",
        "PcfIamUserAccessKey",
        "PcfIamUserSecretAccessKey",
        "PcfVpc",
        "PcfVmsSecurityGroupId",
        "PcfOpsManagerAdminPassword",
        "PcfOpsManagerS3Bucket",
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
        "PcfElasticRuntimeS3ResourcesBucket",
        "PcfNumberOfAZs",
        "PcfCustomResourceSQSQueueUrl",
        "PcfWaitHandle",
        "PcfOpsManagerInstanceIP"
    ]

    def __init__(self):
        self.debug = False
        self.opsman_user = 'admin'

        self.set_versions_and_buckets()
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
    def pcf_opsmanageradminpassword(self):
        return self.parameters["PcfOpsManagerAdminPassword"]

    @property
    def pcf_opsmanagers3bucket(self):
        return self.parameters["PcfOpsManagerS3Bucket"]

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
    def pcf_pcfnumberofazs(self):
        return int(self.parameters["PcfNumberOfAZs"])

    @property
    def pcf_pcfcustomresourcesqsqueueurl(self):
        return self.parameters["PcfCustomResourceSQSQueueUrl"]

    @property
    def pcf_pcfwaithandle(self):
        return self.parameters["PcfWaitHandle"]

    @property
    def pcf_pcfopsmanagerinstanceip(self):
        return self.parameters["PcfOpsManagerInstanceIP"]

    @property
    def pcf_input_pivnettoken(self):
        return self.input_parameters["PivnetToken"]

    @property
    def pcf_input_pcfkeypair(self):
        return self.input_parameters["PCFKeyPair"]

    @property
    def pcf_input_adminemail(self):
        return self.input_parameters["AdminEmail"]

    @property
    def pcf_input_elbprefix(self):
        return self.input_parameters["ElbPrefix"]

    @property
    def pcf_input_hostedzoneid(self):
        return self.input_parameters["HostedZoneId"]

    @property
    def pcf_input_domain(self):
        return self.input_parameters["Domain"]

    @property
    def pcf_input_skipsslvalidation(self):
        return self.input_parameters["SkipSSLValidation"]

    @property
    def opsman_url(self):
        return "https://opsman.{}".format(self.pcf_input_domain)

    def set_versions_and_buckets(self):
        self.ops_manager_version = ops_manager_version
        self.ert_version = ert_version
        self.aws_broker_version = aws_broker_version
        self.tile_bucket_region = tile_bucket_region
        self.tile_bucket_s3_name = tile_bucket_s3_name

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
