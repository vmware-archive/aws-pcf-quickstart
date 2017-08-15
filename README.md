# AWS Quickstart

Launch PCF on AWS with a single click.

See the docs (link todo) for account and launch pre-reqs.

# Running
To run it without any template or code changes:

1. Create an s3 bucket. This would be set as `Quick Start S3 Bucket Name`
1. Get the templates from  https://github.com/cf-platform-eng/quickstart-pivotal-cloudfoundry/blob/develop/templates/ and copy to 
    * `s3://pivotal/cloudfoundry/latest/templates/cloud-formation.template`
    * `s3://pivotal/cloudfoundry/latest/templates/ops-manager.template`
    * Make templates public
1. Get the `quickstart.tgz` from https://github.com/cf-platform-eng/quickstart-pivotal-cloudfoundry/blob/develop/scripts/ and copy to   
    * `s3://pivotal/cloudfoundry/latest/scripts/quickstart.tgz`
    * Make `quickstart.tgz` public
1. Locally download the template `pivotal-cloudfoundry.template` from https://github.com/cf-platform-eng/quickstart-pivotal-cloudfoundry/blob/develop/templates/
1. Create a new stack: https://console.aws.amazon.com/cloudformation by uploading the template above.
1. Be sure to toggle `ForwardLogOutput` to `true` in development, to get feedback on changes in the event of failure
    * View the logs https://console.aws.amazon.com/cloudwatch/ (assuming `ForwardLogOutput` is set to `true`)
1. The full run takes ~2.5 hours. Once the `MyCustomBOSH` resource is completed, you can view installation progress from `https://opsman.[template domain]`

# Dev

The project requires Python 3. Install requirements with

```bash
pip install -r requirements.txt
```

Run the unit tests with
```bash
python -m unittest discover -v -s ./lib -p '*_test.py'
```

### Running with Custom Code

1. Download the linux release of `om` from https://github.com/pivotal-cf/om/releases, move it to `./bin/om`, and `chmod +x ./bin/om`
1. Download the linux release of `pivnet` from https://github.com/pivotal-cf/pivnet-cli/releases, move it to `./bin/pivnet`, and `chmod +x ./bin/pivnet`
1. vendor the dependencies
    * `pip download --no-binary :all: --dest vendor -r requirements.txt`
1. tar up the repo with
    * `tar -czvf aws-quickstart.tgz aws-quickstart`
1. Follow the running instructions, using your customized `quickstart.tgz`

### Running with Custom Templates

To launch the locally with different templates
* Get the instantiated out `pivotal-cloudfoundry.template` from
    * https://github.com/cf-platform-eng/quickstart-pivotal-cloudfoundry/blob/develop/templates/
* To make changes to the OpsManagerTemplate or CloudFoundryTemplate (`ops-manager.template` & `cloud-formation.template`)
    1. Get them from https://github.com/cf-platform-eng/quickstart-pivotal-cloudfoundry/blob/develop/templates/
    1. upload them to an s3 bucket
    1. Make them public
    1. When filling out the CloudFormation params, set OpsManagerTemplate / CloudFoundryTemplate locations to these new s3 urls 
* To use different quickstart code

## Pull requests
### Template
To Pull request back changes to `quickstart-template.yml`, be sure to change the template that renders this file, `./templates/quickstart-template.j2.yml`

# CI

There's a single pipeline that runs unit the unit tests all the way through publishing the boostrap AMI and
making a pull request back to https://github.com/aws-quickstart/quickstart-pivotal-cloudfoundry.

`./ci/pipeline-all-in-one.yml`

This pipeline invokes the various scripts in `./ci`

### Docker

Building the pipeline image
```bash
docker build ci -t cfplatformeng/quickstart-ci
docker tag cfplatformeng/quickstart-ci cfplatformeng/quickstart-ci:1 #where 1 is the tag version number
docker push cfplatformeng/quickstart-ci
```

# Contributing
We welcome comments, questions, and contributions from community members. Please consider the following ways to contribute:

* File Github issues for questions, bugs and new features and comment and vote on the ones that you are interested in.
* If you want to contribute code, please make your code changes on a fork of this repository and submit a pull request to the master branch of tile-generator. We strongly suggest that you first file an issue to let us know of your intent, or comment on the issue you are planning to address.
