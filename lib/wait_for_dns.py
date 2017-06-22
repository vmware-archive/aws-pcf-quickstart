import socket
import time

import settings


def check_dns(domain: str):
    try:
        return socket.gethostbyname(domain)
    except socket.gaierror:
        return ""


def wait_for_dns(my_settings: settings.Settings):
    while True:
        domain = "opsman.{}".format(my_settings.pcf_input_domain())
        print("Checking DNS entry {}".format(domain))
        ip = check_dns(domain)
        if ip == my_settings.pcf_pcfopsmanagerinstanceip:
            return 0
        else:
            time.sleep(5)
