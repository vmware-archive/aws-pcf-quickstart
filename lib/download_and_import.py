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

import glob

import hashlib
import os

import om_manager
import settings
import util


def upload_stemcell(my_settings: settings.Settings, path: str):
    for stemcell in os.listdir(path):
        if stemcell.endswith(".tgz"):
            print("uploading stemcell {0}".format(stemcell))
            cmd = om_manager.get_om_with_auth(my_settings) + [
                "upload-stemcell",
                "-s", os.path.join(path, stemcell)]
            out, err, exit_code = util.exponential_backoff_cmd(cmd)
            if exit_code != 0:
                return out, err, exit_code

    return "", "", 0


def upload_assets(my_settings: settings.Settings, path: str):
    for tile in os.listdir(path):
        if tile.endswith(".pivotal"):
            print("uploading product {0}".format(tile))

            cmd = om_manager.get_om_with_auth(my_settings) + [
                "-r", "3600",
                "upload-product",
                "-p", os.path.join(path, tile)]
            out, err, exit_code = util.exponential_backoff_cmd(cmd)
            if exit_code != 0:
                return out, err, exit_code

    return "", "", 0


def download_assets(my_settings: settings.Settings, path: str):
    cmd = ["pivnet",
           "login",
           "--api-token", my_settings.pcf_input_pivnettoken]
    util.exponential_backoff_cmd(cmd)

    out, err, exit_code = do_pivnet_download(
        'stemcells-ubuntu-xenial',
        my_settings.stemcell_release_version,
        '*aws*.tgz',
        my_settings.stemcell_release_sha256,
        path
    )
    if exit_code != 0:
        return out, err, exit_code
    return do_pivnet_download(
        'cf',
        my_settings.ert_release_version,
        'cf*.pivotal',
        my_settings.ert_release_sha256,
        path
    )


def do_pivnet_download(slug: str, version: str, tile_glob: str, sha256: str, path: str):
    cmd = ["pivnet",
           "download-product-files",
           "-p", slug,
           "-r", version,
           "-g", tile_glob,
           "-d", path]
    out, err, exit_code = util.exponential_backoff_cmd(cmd)
    if exit_code != 0:
        return out, err, exit_code

    paths = glob.glob("{}/{}".format(path, tile_glob))
    if len(paths) != 1:
        return "Issue finding tiles on disk after download", "", 1

    return "", "", verify_sha256(paths[0], sha256)


def verify_sha256(filename, sha256):
    calculated_sha_256 = generate_sha256(filename)
    if sha256.strip() == calculated_sha_256.strip():
        return 0
    else:
        return 1


def generate_sha256(filename):
    buf_size = 65536
    sha256 = hashlib.sha256()

    with open(filename, 'rb') as f:
        while True:
            data = f.read(buf_size)
            if not data:
                break
            sha256.update(data)

    sha = sha256.hexdigest()
    print("SHA256: {0}".format(sha))
    return sha
