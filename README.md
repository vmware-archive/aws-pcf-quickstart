# AWS Quickstart

Launch PCF on AWS with a single click.

See the docs (link todo) for account and launch pre-reqs.

# Launch
To run without any template or code changes:

1. Download the template `pivotal-cloudfoundry.template` from https://github.com/cf-platform-eng/quickstart-pivotal-cloudfoundry/blob/develop/templates/
1. Create a new stack at https://console.aws.amazon.com/cloudformation by uploading `pivotal-cloudfoundry.template`
    * Set `Quick Start S3 Bucket Name` to `aws-pcf-quickstart-templates`
    * To toggle `Forward Log Output` to `true` to get feedback on changes in the event of failure
    * Customize other parameters as needed per docs     
1. The full run takes ~2.5 hours. Once the `MyCustomBOSH` resource is completed, you can view installation progress from `https://opsman.[domain paramater value]`
    * View the logs https://console.aws.amazon.com/cloudwatch/

# Dev

The project requires Python 3. Install requirements with

```bash
pip install -r requirements.txt
```

Run the unit tests with
```bash
python -m unittest discover -v -s ./lib -p '*_test.py'
```

### Launch with Changes

#### Building quickstart.tgz
1. Download the linux release of `om` from https://github.com/pivotal-cf/om/releases, move it to `bin/om`, and `chmod +x ./bin/om`
1. Download the linux release of `pivnet` from https://github.com/pivotal-cf/pivnet-cli/releases, move it to `bin/pivnet`, and `chmod +x ./bin/pivnet`
1. vendor the dependencies
    * `pip download --no-binary :all: --dest vendor -r requirements.txt`
1. tar up the repo with
    * `tar -czvf aws-quickstart.tgz aws-quickstart`
1. Follow the running instructions, using your customized `quickstart.tgz`

#### Create Stack
1. Create an s3 bucket
1. Upload templates
    * `cloudformation/cloudformation.json` to `[s3 bucket]/quickstart-pivotal-cloudfoundry/templates/cloud-formation.template`
    * `cloudformation/ops-manager.json` to  `[s3 bucket]/quickstart-pivotal-cloudfoundry/templates/ops-manager.template`
    * Make both templates public
1. Copy your custom `quickstart.tgz`
    * `[s3 bucket]/quickstart-pivotal-cloudfoundry/scripts/quickstart.tgz`
    * Make `quickstart.tgz` public
1. Download the template `pivotal-cloudfoundry.template` from https://github.com/cf-platform-eng/quickstart-pivotal-cloudfoundry/blob/develop/templates/
    * To PR any changes to `pivotal-cloudfoundry.template`, modify `templates/quickstart-template.j2.yml` 
1. Create a new stack https://console.aws.amazon.com/cloudformation by uploading `pivotal-cloudfoundry.template`
    * Set `Quick Start S3 Bucket Name` to the bucket you created
    * To toggle `Forward Log Output` to `true`
    * Customize other parameters as needed per docs     
1. The full run takes ~2.5 hours. Once the `MyCustomBOSH` resource is completed, you can view installation progress from `https://opsman.[template domain]`

# Contributing
We welcome comments, questions, and contributions from community members. Please consider the following ways to contribute:

* File Github issues for questions, bugs and new features and comment and vote on the ones that you are interested in.
* If you want to contribute code, please make your code changes on a fork of this repository and submit a pull request to the master branch. We strongly suggest that you first file an issue to let us know of your intent, or comment on the issue you are planning to address.
