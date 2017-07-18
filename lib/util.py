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


def exponential_backoff_cmd(cmd, debug):
    return exponential_backoff(
        functools.partial(run_command, cmd, debug),
        check_exit_code,
    )


def run_command(cmd: str, debug_mode):
    print("Running: {}".format(cmd))
    # todo: delete debug mode
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
