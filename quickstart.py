import datetime
import os
import sys
import time

import click

PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, os.path.join(PATH, 'lib'))

from lib import settings, om_manager


@click.group()
@click.pass_context
def cli(ctx):
    my_settings = settings.Settings()
    ctx.obj['settings'] = my_settings
    # ctx.obj['gcp'] = gcp.GCP(my_settings, vars_file, state_file, 'terraforming-gcp', 'overrides')
    pass


@cli.command('configure-opsman-auth')
@click.pass_context
def config_opsman_auth_cmd(ctx):
    sys.exit(time_cmd(om_manager.config_opsman_auth, ctx.obj['settings']))


def time_cmd(cmd, *args):
    cmd_name = cmd.__name__
    print("Starting {}".format(cmd_name))
    start = time.time()
    exit_code = cmd(*args)
    end = time.time()
    print("Duration for {}: {}".format(cmd_name, datetime.timedelta(seconds=end - start)))
    if exit_code != 0:
        print("{} failed".format(cmd_name))
    return exit_code


if __name__ == "__main__":
    cli(obj={})
