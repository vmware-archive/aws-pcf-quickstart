from subprocess import call

from jinja2 import Template
import om_manager
import settings
import util
from settings import Settings


def configure_ert(my_settings: Settings):
    exit_code = om_manager.stage_product("cf", my_settings)
    if exit_code != 0:
        print("Failed to stage ERT")
        return exit_code

    exit_code = configure_tile_az(gcp, my_settings, 'cf')
    if exit_code != 0:
        print("Failed to configure az ERT")
        return exit_code

    exit_code = configure_ert_config(gcp, my_settings)
    if exit_code != 0:
        print("Failed to configure ERT")
        return exit_code

    return configure_ert_resources(my_settings)


def configure_ert_resources(my_settings: Settings):
    ert_resource_ctx = {
        "router_lb_name": [
            "tcp:{env_name}-cf-ws".format(env_name=my_settings.name),
            "http:{env_name}-httpslb".format(env_name=my_settings.name)
        ]
    }
    with open("templates/gcp_ert_resources_config.j2.json", 'r') as f:
        ert_resource_template = Template(f.read())
    ert_resource_config = util.format_om_json_str(ert_resource_template.render(ert_resource_ctx))
    cmd = "{om_with_auth} configure-product -n cf -pr '{ert_resources}'".format(
        om_with_auth=settings.get_om_with_auth(my_settings),
        ert_resources=ert_resource_config
    )
    return call(cmd, shell=True)


def configure_ert_config(gcp, my_settings: Settings):
    ert_config_template_ctx = {
        "env_name": my_settings.name,
        "gcloud_sql_instance_ip": gcp.get_gcloud_sql_instance_ip(),
        "gcloud_sql_instance_username": my_settings.ert_sql_db_username,
        "gcloud_sql_instance_password": my_settings.ert_sql_db_password,
        "pcf_ert_domain": "{}.{}".format(my_settings.name, my_settings.dns_suffix),
        "gcp_storage_access_key": gcp.storage_access_key,
        "gcp_storage_secret_key": gcp.storage_secret
    }
    with open("templates/gcp_ert_config.j2.json", 'r') as f:
        ert_template = Template(f.read())
    ert_config = util.format_om_json_str(ert_template.render(ert_config_template_ctx))
    cmd = "{om_with_auth} configure-product -n cf -p '{ert_config}'".format(
        om_with_auth=settings.get_om_with_auth(my_settings),
        ert_config=ert_config
    )
    return call(cmd, shell=True)


def configure_tile_az(my_settings: Settings, tile_name: str):
    az_template_ctx = {
        "singleton_availability_zone": my_settings.zones[0],
        "zones": my_settings.zones
    }
    with open("templates/ert_az_config.j2.json", 'r') as f:
        redis_az_template = Template(f.read())
    az_config = util.format_om_json_str(redis_az_template.render(az_template_ctx))
    cmd = "{om_with_auth} configure-product -n {tile_name} -pn '{az_config}'".format(
        om_with_auth=settings.get_om_with_auth(my_settings),
        tile_name=tile_name,
        az_config=az_config
    )

    return call(cmd, shell=True)
