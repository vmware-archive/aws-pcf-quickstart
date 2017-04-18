import os
import json

output_file = "/tmp/pcf-stack.json"

class Settings:
    def __init__(self):
        with open(output_file) as output_json:
            stack_output = json.load(output_json)
            stacks = stack_output.get("Stacks")
            if not stacks:
                raise ValueError('{} should conform to {"Stacks":[{....}]}')
            self.stack = stacks[0]
            if not self.stack:
                raise ValueError('{} should conform to {"Stacks":[{....}]}')


        self.ert_sql_db_password = self.find_output("PcfRdsPassword")
        self.ert_sql_db_username = self.find_output("PcfRdsUsername")

        self.dns_suffix = os.environ['DNS_SUFFIX']
        self.ops_manager_version = os.environ['OPS_MANAGER_VERSION']
        # use elb url, output from cloudformation template
        self.opsman_url = os.environ['OPS_MANAGER_URL']
        self.opsman_user = 'admin'
        # todo: password charset validation?
        self.opsman_password = os.environ['OPS_MANAGER_ADMIN_PASSWORD']

    def get_fully_qualified_domain(self):
        return self.dns_suffix

    def find_output(self, name:str):
        for output in self.stack.get("Outputs"):
            key = output.get("OutputKey", None)
            if key == name:
                return output.get("OutputValue")

        return None


def get_om_with_auth(settings: Settings):
    return "om -k --target {url} --username '{username}' --password '{password}'".format(
        url=settings.opsman_url,
        username=settings.opsman_user,
        password=settings.opsman_password
    )
