# aws-pcf-quickstart
#
# Copyright (c) 2017-Present Pivotal Software, Inc. All Rights Reserved.
#
# This program and the accompanying materials are made available under
# the terms of the under the Apache License, Version 2.0 (the "License”);
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

import time
import subprocess
import functools

max_retries = 5


def exponential_backoff(fun, test, attempt=0):
    result = fun()
    print("Running {}, got {}".format(fun, result))
    if test(result):
        return result
    elif attempt < max_retries:
        print("Sleeping {}".format(attempt ** 3))
        time.sleep(attempt ** 3)
        result = exponential_backoff(fun, test, attempt + 1)
    return result


def check_exit_code(result):
    out, err, returncode = result
    if out != "":
        print("out: {}".format(out))
    if err != "":
        print("error: {}".format(err))

    return returncode == 0


def exponential_backoff_cmd(cmd):
    return exponential_backoff(
        functools.partial(run_command, cmd),
        check_exit_code,
    )


def run_command(cmd: str):
    print("Running: {}".format(cmd))
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out_bytes, err_bytes = p.communicate()
    out = out_bytes.decode("utf-8").strip()
    err = err_bytes.decode("utf-8").strip()
    return out, err, p.returncode
