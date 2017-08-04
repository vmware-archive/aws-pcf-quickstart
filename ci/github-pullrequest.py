import json
import sys

import os
import requests

token = os.environ['GITHUB_ACCESS_TOKEN']

with open('version/version') as version_file:
    version = version_file.read()

print("Making PR request to this release {}".format(version))
response = requests.post(
    url='https://api.github.com/repos/aws-quickstart/quickstart-pivotal-cloudfoundry/pulls',
    data=json.dumps({
        "title": "PR via CI updating to release {}".format(version),
        "body": "Please pull this in!",
        "head": "cf-platform-eng:develop",
        "base": "develop"
    }),
    headers={
        'Authorization': 'Token {}'.format(token),
        'Content-Type': 'application/json',
    }
)

print(response.status_code)
print(response)

sys.exit(response.status_code < 300)
