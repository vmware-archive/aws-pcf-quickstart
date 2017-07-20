import os
import settings
import om_manager
import re
import util
import hashlib


# def upload_stemcell(my_settings: settings.Settings, path: str):
#     for stemcell in os.listdir(path):
#         if stemcell.endswith(".tgz"):
#             print("uploading stemcell {0}".format(stemcell))
#             cmd = "{om_with_auth} upload-stemcell -s '{path}'".format(
#                 om_with_auth=om_manager.get_om_with_auth(my_settings), path=os.path.join(path, stemcell)
#             )
#             out, err, exit_code = util.exponential_backoff_cmd(cmd, my_settings.debug)
#             if exit_code != 0:
#                 return out, err, exit_code
#
#     return "", "", 0
#
#
# def upload_assets(my_settings: settings.Settings, path: str):
#     for tile in os.listdir(path):
#         if tile.endswith(".pivotal"):
#             print("uploading product {0}".format(tile))
#
#             cmd = "{om_with_auth} -r 3600 upload-product -p '{path}'".format(
#                 om_with_auth=om_manager.get_om_with_auth(my_settings), path=os.path.join(path, tile))
#
#             out, err, exit_code = util.exponential_backoff_cmd(cmd, my_settings.debug)
#             if exit_code != 0:
#                 return out, err, exit_code
#
#     return "", "", 0
#
#
def download_asset(my_settings: settings.Settings, path: str):
    cmd = "pivnet login --api-token={token}".format(token=my_settings.pcf_input_pivnettoken)
    util.exponential_backoff_cmd(cmd, False)
    out, err, exit_code = do_pivnet_download('cf', '1.10.8', 'cf*.pivotal', '70070bf22231d9971c97b8deb8c4cd5ba990d24101e5398d0ccc70778060dbea')
    if exit_code != 0:
        return out, err, exit_code
    return do_pivnet_download('stemcells', '3363.20', '*aws*.tgz', 'ece6b9aaa4af20c180c446582bfa8e7d29681e2aac06c5d3d978a92c84432237')


def do_pivnet_download(slug: str, version: str, glob: str, sha256: str):
    dir = '/home/ubuntu/tiles'
    cmd = "./pivnet download-product-files -p {slug} -r {version} -g '{glob}' -d '{dir}'".format(
        slug=slug, version=version, glob=glob, dir=dir
    )
    for file_name in os.listdir('/home/ubuntu/tiles'):
        if re.match(glob, file_name):
            file_path_file_name = "{dir}/{file_name}".format(
                dir=dir, file_name=file_name
            )
            verify_sha256(file_path_file_name, sha256)
    return util.exponential_backoff_cmd(cmd, False)


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
