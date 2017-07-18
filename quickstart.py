import os
import sys
import functools

PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, os.path.join(PATH, 'lib'))

from lib import settings, om_manager, configure_opsman_director, configure_ert, sqs, wait_condition, wait_for_dns
from lib import util, accept_eula

my_settings = settings.Settings()
asset_path = '/home/ubuntu/tiles'

max_retries = 5


def test_exit_code_success(exit_code):
    print("exit_code {}".format(exit_code))
    return exit_code == 0


def check_return_code(out, err, return_code, step_name):
    print("Ran: {}; exit code: {}".format(step_name, exit_code))
    if return_code != 0:
        util.exponential_backoff(
            functools.partial(sqs.report_cr_creation_failure, my_settings, out),
            test_exit_code_success
        )
        sys.exit(1)


out, err, exit_code = accept_eula.accept_ert_eula(my_settings)
check_return_code(out, err, exit_code, 'accept_eula')

exit_code = wait_for_dns.wait_for_dns(my_settings)
check_return_code("todo", "todo", exit_code, 'wait_for_dns')

out, err, exit_code = om_manager.config_opsman_auth(my_settings)
check_return_code(out, err, exit_code, 'config_opsman_auth')

out, err, exit_code = configure_opsman_director.configure_opsman_director(my_settings)
check_return_code(out, err, exit_code, 'configure_opsman_director')
out, err, exit_code = om_manager.apply_changes(my_settings)
check_return_code(out, err, exit_code, 'apply_changes')

sqs.report_cr_creation_success(my_settings, 'MyCustomBOSH')

out, err, exit_code = om_manager.upload_assets(my_settings, asset_path)
check_return_code(out, err, exit_code, 'upload_assets')
out, err, exit_code = om_manager.upload_stemcell(my_settings, asset_path)
check_return_code(out, err, exit_code, 'upload_stemcell')
out, err, exit_code = configure_ert.configure_ert(my_settings)
check_return_code(out, err, exit_code, 'configure_ert')
out, err, exit_code = om_manager.apply_changes(my_settings)
check_return_code(out, err, exit_code, 'apply_changes')

wait_condition.report_success(my_settings, "Successfully deployed Elastic Runtime")
