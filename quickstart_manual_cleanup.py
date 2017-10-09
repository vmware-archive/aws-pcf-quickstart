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

import os
import sys

PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, os.path.join(PATH, 'lib'))

from lib import settings, sqs, wait_condition

my_settings = settings.Settings()

# Toggle some signal to true to manually signal
report_cr_creation_success = False
report_cr_creation_failure = False
report_wc_success = False
report_wc_failure = False

if report_cr_creation_success:
    print("Reporting custom resource SUCCESS")
    sqs.report_cr_deletion_success(my_settings, "manual success", "MyCustomBOSH")
    sys.exit(0)

if report_cr_creation_failure:
    print("Reporting custom resource FAILURE")
    sqs.report_cr_creation_failure(my_settings, "manual failure", "MyCustomBOSH")
    sys.exit(0)

if report_wc_success:
    print("Reporting wait condition SUCCESS")
    wait_condition.report_success(my_settings, "manual success")
    sys.exit(0)

if report_wc_failure:
    print("Reporting wait condition FAILURE")
    wait_condition.report_failure(my_settings, "manual failure")
    sys.exit(0)

print("No signal specified, nothing done")
sys.exit(1)
