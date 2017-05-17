#!/usr/bin/env python3

import datetime
import os
import sys
import time

PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, os.path.join(PATH, 'lib'))

poll_interval = 30

from lib import settings, delete_everything


def main():
    while (True):
        if os.path.exists("/tmp/fake_sqs_delete"):
            print("Doing deletion")
            do_deletion()
        else:
            print("Polling again {}".format(datetime.datetime.now()))

        time.sleep(poll_interval)


def do_deletion():
    my_settings = settings.Settings()
    delete_everything.delete_everything(my_settings)


if __name__ == "__main__":
    main()
