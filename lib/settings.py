import os


class Settings:
    def __init__(self):
        self.ert_sql_db_username = os.environ['ERT_SQL_DB_USERNAME']
        self.ert_sql_db_password = os.environ['ERT_SQL_DB_PASSWORD']
        self.dns_suffix = os.environ['DNS_SUFFIX']
        self.ops_manager_version = os.environ['OPS_MANAGER_VERSION']
        # use elb url, output from cloudformation template
        self.opsman_url = os.environ['OPS_MANAGER_URL']
        self.opsman_user = 'admin'
        self.opsman_password = os.environ['OPS_MANAGER_ADMIN_PASSWORD']

    def get_fully_qualified_domain(self):
        return self.dns_suffix


def get_om_with_auth(settings: Settings):
    return "om -k --target {url} --username {username} --password {password}".format(
        url=settings.opsman_url,
        username=settings.opsman_user,
        password=settings.opsman_password
    )
