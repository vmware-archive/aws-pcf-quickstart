# aws-pcf-quickstart
#
# Copyright (c) 2017-Present Pivotal Software, Inc. All Rights Reserved.
#
# This program and the accompanying materials are made available under
# the terms of the under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import functools
import os
import sys

PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, os.path.join(PATH, 'lib'))

from lib import settings, om_manager, configure_opsman_director, configure_ert, sqs, wait_condition
from lib import util, accept_eula, download_and_import

my_settings = settings.Settings()
asset_path = '/home/ubuntu/tiles'

max_retries = 5


def check_exit_code_success(exit_code):
    print("exit_code {}".format(exit_code))
    return exit_code == 0


def check_cr_return_code(out, err, return_code, step_name):
    print("Ran: {}; exit code: {}".format(step_name, exit_code))
    if return_code != 0:
        util.exponential_backoff(
            functools.partial(sqs.report_cr_creation_failure, my_settings, out),
            check_exit_code_success
        )
        sys.exit(1)


def check_waitcondition_return_code(out, err, return_code, step_name):
    print("Ran: {}; exit code: {}".format(step_name, exit_code))
    if return_code != 0:
        util.exponential_backoff(
            functools.partial(wait_condition.report_failure, my_settings, out),
            check_exit_code_success
        )
        sys.exit(1)


out, err, exit_code = accept_eula.accept_eulas(my_settings)
check_cr_return_code(out, err, exit_code, 'accept_eula')

out, err, exit_code = om_manager.config_opsman_auth(my_settings)
check_cr_return_code(out, err, exit_code, 'config_opsman_auth')

out, err, exit_code = configure_opsman_director.configure_opsman_director(my_settings)
check_cr_return_code(out, err, exit_code, 'configure_opsman_director')
my_settings.toggle_resources_created()
out, err, exit_code = om_manager.apply_changes(my_settings)
check_cr_return_code(out, err, exit_code, 'apply_changes')

sqs.report_cr_creation_success(my_settings, 'MyCustomBOSH')

out, err, exit_code = download_and_import.download_assets(my_settings, asset_path)
check_waitcondition_return_code(out, err, exit_code, 'download_assets')
out, err, exit_code = download_and_import.upload_assets(my_settings, asset_path)
check_waitcondition_return_code(out, err, exit_code, 'upload_assets')
out, err, exit_code = download_and_import.upload_stemcell(my_settings, asset_path)
check_waitcondition_return_code(out, err, exit_code, 'upload_stemcell')

out, err, exit_code = configure_ert.configure_ert(my_settings)
check_waitcondition_return_code(out, err, exit_code, 'configure_ert')
out, err, exit_code = om_manager.apply_changes(my_settings)
check_waitcondition_return_code(out, err, exit_code, 'apply_changes')

wait_condition.report_success(my_settings, "Successfully deployed Elastic Runtime")
