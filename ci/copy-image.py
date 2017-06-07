#! /usr/bin/env python3

import json
import os
import sys

import boto3

destination_regions = [
    'us-west-1', 'us-west-2'
]


def main(argv):
    with open('./ami-version/version', 'r') as version_file:
        ami_version = version_file.read()

    with open('./packer-result/packer-result-{}.json'.format(ami_version), 'r') as packer_result_file:
        packer_result = json.loads(packer_result_file.read())

    print("Packer result")
    print(json.dumps(packer_result, indent="  "))

    builds = packer_result.get('builds')
    if len(builds) != 1:
        print("Packer result didn't match expected format")
        sys.exit(1)
    artifact_id = builds[0].get('artifact_id')
    source_region, source_ami_id = artifact_id.split(":")

    mapping = {
        source_region: source_ami_id
    }
    for destination_region in destination_regions:
        if source_region == destination_region:
            continue
        client = boto3.client(
            service_name='ec2',
            region_name=destination_region,
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
        )

        response = client.copy_image(
            SourceRegion=source_region,
            SourceImageId=source_ami_id,
            Name="pcf bootstrap {}".format(ami_version)
        )
        new_image_id = response.get('ImageId')
        mapping[destination_region] = new_image_id

    print("Final mapping")
    json.dumps(mapping, indent="  ")
    with open('./output/ami-mapping-{}.json'.format(ami_version), 'w') as ami_mapping_file:
        json.dump(mapping, ami_mapping_file, indent="  ")


if __name__ == "__main__":
    main(sys.argv)
