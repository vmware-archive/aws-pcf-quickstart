import settings
import boto3
import sys
import threading
import hashlib


class ProgressPercentage(object):
    def __init__(self, filename):
        self._filename = filename
        self._seen_so_far = 0
        self._lock = threading.Lock()
    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            # sys.stdout.write(
            #     "\r%s --> %s bytes transferred \n" % (
            #         self._filename, self._seen_so_far))
            sys.stdout.flush()


def download_tiles(my_settings: settings.Settings):
    s3 = boto3.client(
        service_name='s3', region_name=my_settings.tile_bucket_region,
        aws_access_key_id=my_settings.tile_bucket_s3_access_key,
        aws_secret_access_key=my_settings.tile_bucket_s3_secret_access_key
    )
    return download_ert(s3, my_settings)


def download_ert(s3, my_settings: settings.Settings):
    # todo: what sorts of errors does this guy give back?

    file_name = "cf-{}.pivotal".format(my_settings.ert_version)
    sha256_file_name = "cf-{}.sha256.txt".format(my_settings.ert_version)

    dest_dir = "/tmp/{}".format(file_name)
    sha_dir = "/tmp/{}".format(sha256_file_name)

    s3.download_file(my_settings.tile_bucket_s3_name, sha256_file_name, sha_dir,
                              Callback=ProgressPercentage(sha_dir))
    s3.download_file(my_settings.tile_bucket_s3_name, file_name, dest_dir, Callback=ProgressPercentage(dest_dir))

    with open(sha_dir, 'r') as f:
        sha_256 = f.read()
    return verify_sha256(dest_dir, sha_256)


def verify_sha256(filename, sha256):
    result_sha_256 = generate_sha256(filename)
    if sha256.strip() == result_sha_256.strip():
        return 0
    else:
        return 1

def generate_sha256(filename):

    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
    sha256 = hashlib.sha256()

    with open(filename, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha256.update(data)

    sha = sha256.hexdigest()
    print("SHA256: {0}".format(sha))
    return sha
