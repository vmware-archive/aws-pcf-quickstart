import json
import os
import sys
import requests

metadata_file_path = '../ert-tile/metadata.json'
pivnet_token = os.environ['PIVNET_TOKEN']

with open(metadata_file_path, 'r') as metadata_ert_raw:
    metadata_ert = json.load(metadata_ert_raw)
    print("metadata:")
    print(json.dumps(metadata_ert, indent="  "))

    ert_product_files = metadata_ert.get("ProductFiles")
    ert_tile_product_file = None
    for product_file in ert_product_files:
        if product_file.get("File") == "Pivotal Application Service":
            ert_tile_product_file = product_file
    if not ert_tile_product_file:
        print("Unable to find ert tile in product ert release file list")
        sys.exit(1)

    dependecies = metadata_ert.get("Dependencies")
    stemcell_dependency = None
    for dependency in dependecies:
        dependency_release = dependency.get("Release")
        if dependency_release.get("Product").get("Name") == "Stemcells for PCF (Ubuntu Xenial)":
            stemcell_dependency = dependency_release
    if not stemcell_dependency:
        print("Unable to find stemcell in dependency list")
        sys.exit(1)

    stemcell_pivnet_url = "https://network.pivotal.io/api/v2/products/stemcells-ubuntu-xenial/releases/{}".format(
        stemcell_dependency.get("ID")
    )

    stemcell_response = requests.get(
        url=stemcell_pivnet_url,
        headers={
            'Authorization': 'Token {}'.format(pivnet_token),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    )
    if stemcell_response.status_code != 200:
        print("Failed getting stemcell data from data")
        print(stemcell_response)
        print(stemcell_response.status_code)
        sys.exit(1)
    metadata_stemcell = stemcell_response.json()

    stemcell_product_file = None
    for product_file in metadata_stemcell.get("product_files"):
        if "aws-xen" in product_file.get("aws_object_key"):
            # Make sure that this selection doesn't catch more than one file
            if stemcell_product_file:
                print("Too many files matched selection in stemcell release file list")
                sys.exit(1)
            stemcell_product_file = product_file
    if not stemcell_product_file:
        print("Unable to find stemcell in product stemcell release file list")
        sys.exit(1)

    ert_release = metadata_ert.get("Release")

    config = {
        "ert": {
            "id": ert_release.get("ID"),
            "version": ert_release.get("Version"),
            "releaseDate": ert_release.get("ReleaseDate"),
            "sha256": ert_tile_product_file.get("SHA256")
        },
        "stemcell": {
            "id": stemcell_dependency.get("ID"),
            "version": stemcell_dependency.get("Version"),
            "releaseDate": metadata_stemcell.get("release_date"),
            "sha256": stemcell_product_file.get("sha256"),
        }
    }

    with open("version_config.json", "w") as config_output_file:
        json.dump(config, config_output_file, indent="  ")
