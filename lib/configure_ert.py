from subprocess import call

from jinja2 import Template

import om_manager
import settings
from settings import Settings


def configure_ert(my_settings: Settings):
    exit_code = om_manager.stage_product("cf", my_settings)
    if exit_code != 0:
        print("Failed to stage ERT")
        return exit_code

    exit_code = configure_tile_az(my_settings, 'cf')
    if exit_code != 0:
        print("Failed to configure az ERT")
        return exit_code

    exit_code = configure_ert_config(my_settings)
    if exit_code != 0:
        print("Failed to configure ERT")
        return exit_code

    exit_code = configure_ert_resources(my_settings)
    if exit_code != 0:
        print("Failed to configure ERT")
        return exit_code

    return create_required_databases(my_settings)


def configure_ert_resources(my_settings: Settings):
    ert_resource_ctx = {
        "router_lb_name": "{stack_name}{elb_prefix}".format(
            stack_name=my_settings.stack_name, elb_prefix=my_settings.elb_prefix
        ),
    }
    with open("templates/ert_resources_config.j2.json", 'r') as f:
        ert_resource_template = Template(f.read())
    ert_resource_config = om_manager.format_om_json_str(ert_resource_template.render(ert_resource_ctx))
    cmd = "{om_with_auth} configure-product -n cf -pr '{ert_resources}'".format(
        om_with_auth=settings.get_om_with_auth(my_settings),
        ert_resources=ert_resource_config
    )
    return call(cmd, shell=True)


def configure_ert_config(my_settings: Settings):
    ert_config_template_ctx = {
        "pcf_rds_address": my_settings.pcf_rds_address,
        "pcf_rds_username": my_settings.pcf_rds_username,
        "dns_suffix": my_settings.dns_suffix,
        "pcf_rds_password": my_settings.pcf_rds_password,
        "admin_email": my_settings.admin_email,
        "pcf_elastic_runtime_s3_buildpacks_bucket": my_settings.pcf_elastic_runtime_s3_buildpacks_bucket,
        "pcf_elastic_runtime_s3_droplets_bucket": my_settings.pcf_elastic_runtime_s3_droplets_bucket,
        "pcf_elastic_runtime_s3_packages_bucket": my_settings.pcf_elastic_runtime_s3_packages_bucket,
        "pcf_elastic_runtime_s3_resources_bucket": my_settings.pcf_elastic_runtime_s3_resources_bucket,
        "pcf_iam_access_key_id": my_settings.pcf_iam_access_key_id,
        "pcf_iam_secret_access_key": my_settings.pcf_iam_secret_access_key,
    }
    with open("templates/ert_config.j2.json", 'r') as f:
        ert_template = Template(f.read())
    ert_config = om_manager.format_om_json_str(ert_template.render(ert_config_template_ctx))
    cmd = "{om_with_auth} configure-product -n cf -p '{ert_config}'".format(
        om_with_auth=settings.get_om_with_auth(my_settings),
        ert_config=ert_config
    )
    return om_manager.exponential_backoff(my_settings.debug, cmd)


def configure_tile_az(my_settings: Settings, tile_name: str):
    az_template_ctx = {
        "singleton_availability_zone": my_settings.zones[0],
        "zones": my_settings.zones
    }
    with open("templates/tile_az_config.j2.json", 'r') as f:
        az_template = Template(f.read())
    az_config = om_manager.format_om_json_str(az_template.render(az_template_ctx))
    cmd = "{om_with_auth} configure-product -n {tile_name} -pn '{az_config}'".format(
        om_with_auth=settings.get_om_with_auth(my_settings),
        tile_name=tile_name,
        az_config=az_config
    )

    return om_manager.exponential_backoff(my_settings.debug, cmd)


def create_required_databases(my_settings: Settings):
    cmd = "mysql -h {hostname} --user={username} --port={port} --password={password} < templates/required_dbs.sql".format(
        hostname=my_settings.pcf_rds_address,
        username=my_settings.pcf_rds_username,
        port=my_settings.pcf_rds_port,
        password=my_settings.pcf_rds_password
    )

    return om_manager.exponential_backoff(my_settings.debug, cmd)
