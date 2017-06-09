import datetime
import os
import sys
import time

import click

PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, os.path.join(PATH, 'lib'))

from lib import settings, om_manager, configure_opsman_director, download_tiles, configure_ert, \
    delete_everything


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, debug):
    my_settings = settings.Settings()
    ctx.obj['settings'] = my_settings
    my_settings.debug = debug


@cli.command('configure-opsman-auth')
@click.pass_context
def config_opsman_auth_cmd(ctx):
    sys.exit(time_cmd(om_manager.config_opsman_auth, ctx.obj['settings']))


@cli.command('configure-opsman-director')
@click.pass_context
def config_bosh(ctx):
    sys.exit(time_cmd(configure_opsman_director.configure_opsman_director, ctx.obj['settings']))


@cli.command('apply-changes')
@click.pass_context
def apply_changes(ctx):
    sys.exit(time_cmd(om_manager.apply_changes, ctx.obj['settings']))


@cli.command('download-tiles')
@click.pass_context
def apply_changes(ctx):
    sys.exit(time_cmd(download_tiles.download_tiles, ctx.obj['settings']))


@cli.command('upload-assets')
@click.argument('path')
@click.pass_context
def upload_assets(ctx, path):
    sys.exit(time_cmd(om_manager.upload_assets, ctx.obj['settings'], path))


@cli.command('upload-stemcell')
@click.argument('path')
@click.pass_context
def upload_stemcells(ctx, path):
    sys.exit(time_cmd(om_manager.upload_stemcell, ctx.obj['settings'], path))


@cli.command('configure-ert')
@click.pass_context
def config_ert(ctx):
    sys.exit(time_cmd(configure_ert.configure_ert, ctx.obj['settings']))


@cli.command('curl')
@click.argument('path')
@click.pass_context
def curl(ctx, path):
    sys.exit(time_cmd(om_manager.curl_get, ctx.obj['settings'], path))


@cli.command('delete-everything')
@click.pass_context
def delete(ctx):
    sys.exit(time_cmd(delete_everything.delete_everything, ctx.obj['settings']))


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
