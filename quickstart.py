import os
import sys

PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, os.path.join(PATH, 'lib'))

from lib import settings, om_manager, configure_opsman_director, configure_ert, sqs

my_settings = settings.Settings()

asset_path = '/home/ubuntu/tiles'


def check_return_code(return_code, step_name):
    print("Running {}".format(step_name))
    if return_code != 0:
        sqs.report_cr_creation_failure(my_settings)
        sys.exit(1)


check_return_code(om_manager.config_opsman_auth(my_settings), 'config_opsman_auth')

print("Reporting success early, until we workout how to increase the timeout")
sqs.report_cr_creation_success(my_settings)

check_return_code(configure_opsman_director.configure_opsman_director(my_settings), 'configure_opsman_director')
check_return_code(om_manager.apply_changes(my_settings), 'apply_changes')
check_return_code(om_manager.upload_assets(my_settings, asset_path), 'my_settings')
check_return_code(om_manager.upload_stemcell(my_settings, asset_path), 'my_settings')
check_return_code(configure_ert.configure_ert(my_settings), 'configure_ert')
check_return_code(om_manager.apply_changes(my_settings), 'apply_changes')
