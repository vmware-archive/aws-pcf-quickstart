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

import delete_everything
import settings
import sqs


def check(my_settings: settings.Settings):
    raw_message = sqs.get_messages(my_settings)

    if len(raw_message) < 1:
        print("No message on queue; doing nothing since delete not triggered")
        return
    messages = [sqs.parse_message(m) for m in raw_message]
    delete_messages = [
        m for m in messages if
        m.get('RequestType') == "Delete"
    ]
    if len(delete_messages) < 1:
        print("No message of type Delete")
        return

    out, err, return_code = delete_everything.delete_everything(my_settings)
    for delete_message in delete_messages:
        if return_code != 0:
            sqs.report_cr_deletion_failure(my_settings, delete_message.get('LogicalResourceId'))
        else:
            sqs.report_cr_deletion_success(my_settings, delete_message.get('LogicalResourceId'))
