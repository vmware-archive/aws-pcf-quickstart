from jinja2 import Template

import om_manager
import settings
from settings import Settings


def configure_opsman_director(my_settings: Settings):
    director_config = '{"ntp_servers_string": "0.amazon.pool.ntp.org,1.amazon.pool.ntp.org,2.amazon.pool.ntp.org,3.amazon.pool.ntp.org"}'

    template_ctx = {
        "zones": my_settings.zones,
        "access_key_id": my_settings.pcf_iamuseraccesskey,
        "secret_access_key": my_settings.pcf_iamusersecretaccesskey,
        "vpc_id": my_settings.pcf_vpc,
        "security_group": my_settings.pcf_vmssecuritygroupid,
        "key_pair_name": my_settings.pcf_input_pcfkeypair,
        "ssh_private_key": my_settings.pcf_pcfprivatesshkey.replace("\n", "\\n"),
        "region": my_settings.region,
        "encrypted": "false",
        "vpc_private_subnet_id": my_settings.pcf_privatesubnetid,
        "vpc_private_subnet_az": my_settings.pcf_privatesubnetavailabilityzone,
        "vpc_private_subnet_id2": my_settings.pcf_privatesubnet2id,
        "vpc_private_subnet_az2": my_settings.pcf_privatesubnet2availabilityzone,
        "singleton_availability_zone": my_settings.pcf_privatesubnetavailabilityzone

    }
    with open("templates/bosh_az_config.j2.json", 'r') as f:
        az_template = Template(f.read())
    with open("templates/bosh_network_config.j2.json", 'r') as f:
        network_template = Template(f.read())
    with open("templates/bosh_iaas_config.j2.json", 'r') as f:
        iaas_template = Template(f.read())
    with open("templates/bosh_network_assignment.j2.json", 'r') as f:
        network_assignment_template = Template(f.read())

    az_config = az_template.render(template_ctx).replace("\n", "")
    network_config = network_template.render(template_ctx).replace("\n", "")
    network_assignment_config = network_assignment_template.render(template_ctx).replace("\n", "")
    iaas_config = iaas_template.render(template_ctx).replace("\n", "")

    commands = []
    commands.append("{om_with_auth} configure-bosh --iaas-configuration '{iaas_config}'".format(
        om_with_auth=om_manager.get_om_with_auth(my_settings), iaas_config=iaas_config
    ))
    commands.append("{om_with_auth} configure-bosh --director-configuration '{director_config}'".format(
        om_with_auth=om_manager.get_om_with_auth(my_settings), director_config=director_config
    ))
    commands.append("{om_with_auth} configure-bosh --az-configuration '{az_config}'".format(
        om_with_auth=om_manager.get_om_with_auth(my_settings), az_config=az_config
    ))
    commands.append("{om_with_auth} configure-bosh --networks-configuration '{network_config}'".format(
        om_with_auth=om_manager.get_om_with_auth(my_settings), network_config=network_config
    ))
    commands.append("{om_with_auth} configure-bosh --network-assignment '{network_assignment}'".format(
        om_with_auth=om_manager.get_om_with_auth(my_settings), network_assignment=network_assignment_config
    ))
    for cmd in commands:
        out, err, exit_code = om_manager.run_command(cmd, my_settings.debug)
        if out != "":
            print(out)
        if err != "":
            print(err)
        if exit_code != 0:
            return exit_code

    return 0
