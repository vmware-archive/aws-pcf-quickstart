import threading

import boto3
import hashlib

import settings


class ProgressPercentage(object):
    def __init__(self, filename):
        self._filename = filename
        self._seen_so_far = 0
        self._lock = threading.Lock()
        self.last_print = 0

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount / (1024 * 1024)
            if self._seen_so_far >= (self.last_print + 15):
                self.last_print = self._seen_so_far
                print("{} --> {} MB transferred".format(self._filename, self._seen_so_far))


def download_tiles(my_settings: settings.Settings):
    s3 = boto3.client(
        service_name='s3', region_name=my_settings.tile_bucket_region
    )
    for filename in [
        "cf-{}.pivotal".format(my_settings.ert_version),
        "aws-services-{}.pivotal".format(my_settings.aws_broker_version),
        "light-bosh-stemcell-3363.15-aws-xen-hvm-ubuntu-trusty-go_agent.tgz"
    ]:
        returncode = download_tile(filename, my_settings, s3)
        if returncode != 0:
            return returncode

    return 0


def download_tile(filename, my_settings, s3):
    sha256_filename = filename + '.sha256'
    dest_filename = "/tmp/{}".format(filename)
    dest_sha256_filename = "/tmp/{}".format(sha256_filename)
    s3.download_file(my_settings.tile_bucket_s3_name, sha256_filename, dest_sha256_filename,
                     Callback=ProgressPercentage(dest_sha256_filename))
    s3.download_file(my_settings.tile_bucket_s3_name, filename, dest_filename,
                     Callback=ProgressPercentage(dest_filename))
    with open(dest_sha256_filename, 'r') as f:
        sha_256 = f.read()
    return verify_sha256(dest_filename, sha_256)


def verify_sha256(filename, sha256):
    result_sha_256 = generate_sha256(filename)
    if sha256.strip() == result_sha_256.strip():
        return 0
    else:
        return 1


def generate_sha256(filename):
    buf_size = 65536
    sha256 = hashlib.sha256()

    with open(filename, 'rb') as f:
        data = f.read(buf_size)
        while data:
            sha256.update(data)
            data = f.read(buf_size)

    sha = sha256.hexdigest()
    print("SHA256: {0}".format(sha))
    return sha
