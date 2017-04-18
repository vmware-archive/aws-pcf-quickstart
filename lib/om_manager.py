import subprocess
import time

from settings import Settings

max_retries = 5


def config_opsman_auth(my_settings: Settings, attempt=0):
    cmd = "om -k --target {0} configure-authentication --username {1} --password {2} --decryption-passphrase {3}".format(
        my_settings.opsman_url, my_settings.opsman_user, my_settings.opsman_password,
        my_settings.opsman_password
    )

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out_bytes, err_bytes = p.communicate()
    out = out_bytes.decode("utf-8").strip()
    err = err_bytes.decode("utf-8").strip()

    if p.returncode != 0:
        if out != "":
            print(out)
        if err != "":
            print(err)
        if is_recoverable_error(out) and attempt < max_retries:
            print("Retrying, {}".format(attempt))
            time.sleep(attempt ** 3)
            config_opsman_auth(my_settings, attempt + 1)

    return p.returncode


def is_recoverable_error(err: str):
    recoverable_errors = ["i/o timeout", "connection refused"]
    clean_err = err
    for recoverable_error in recoverable_errors:
        if clean_err.endswith(recoverable_error):
            return True
    return False
