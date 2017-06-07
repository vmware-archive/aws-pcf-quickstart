import json


def main(argv):
    with open('./ami-version/version', 'r') as version_file:
        ami_version = version_file.read()

    with open('./packer-result/packer-result-{}.json'.format(ami_version), 'r') as version_file:
        packer_result = json.loads(version_file.read())

    print(json.dumps(packer_result))
