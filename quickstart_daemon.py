#!/usr/bin/env python3

import os
import sys
import time

PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, os.path.join(PATH, 'lib'))

import delete_check
import settings

poll_interval = 30


def main():
    while (True):
        my_settings = settings.Settings()
        delete_check.check(my_settings)
        time.sleep(poll_interval)


if __name__ == "__main__":
    main()
