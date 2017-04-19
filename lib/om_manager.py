import subprocess
import time

import settings

# todo: spin up a class, don't use package level vars
max_retries = 5


def config_opsman_auth(my_settings: settings.Settings):
    cmd = "om -k --target {0} configure-authentication --username '{1}' --password '{2}' --decryption-passphrase '{3}'".format(
        my_settings.opsman_url, my_settings.opsman_user, my_settings.opsman_password,
        my_settings.opsman_password
    )
    return exponential_backoff(my_settings.debug, cmd)


def exponential_backoff(debug, cmd, attempt=0):
    out, err, returncode = run_command(cmd, debug)
    if out != "":
        print(out)
    if err != "":
        print(err)

    if returncode != 0:
        if is_recoverable_error(out) and attempt < max_retries:
            print("Retrying, {}".format(attempt))
            time.sleep(attempt ** 3)
            returncode = exponential_backoff(debug, cmd, attempt + 1)

    return returncode


def run_command(cmd: str, debug_mode):
    if debug_mode:
        print("Debug mode. Would have run command")
        print("    {}".format(cmd))
        return "", "", 0
    else:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out_bytes, err_bytes = p.communicate()
        out = out_bytes.decode("utf-8").strip()
        err = err_bytes.decode("utf-8").strip()
        return out, err, p.returncode


def apply_changes(my_settings: settings.Settings):
    cmd = "{get_om_with_auth} apply-changes".format(
        get_om_with_auth=settings.get_om_with_auth(my_settings)
    )
    return exponential_backoff(my_settings.debug, cmd)


def is_recoverable_error(err: str):
    recoverable_errors = ["i/o timeout", "connection refused"]
    clean_err = err
    for recoverable_error in recoverable_errors:
        if clean_err.endswith(recoverable_error):
            return True
    return False
