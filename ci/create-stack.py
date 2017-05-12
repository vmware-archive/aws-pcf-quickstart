import jinja2
import os
import sys
from subprocess import call

pcfkeypairprivate = os.environ['AWS_CF_PCFKEYPAIRPRIVATE'],
password = os.environ['AWS_CF_PASSWORD'],
domain = os.environ['AWS_CF_DOMAIN'],
hostedzoneid = os.environ['AWS_CF_HOSTEDZONEID'],
sslcertificatearn = os.environ['AWS_CF_SSLCERTIFICATEARN'],
natkeypair = os.environ['AWS_CF_NATKEYPAIR'],
pivnettoken = os.environ['AWS_CF_PIVNETTOKEN'],

with open('ci/parameters.j2.json', 'r') as template_file:
    template = template_file.read()
    rendered = jinja2.Template(template).render({
        "pcfkeypairprivate": pcfkeypairprivate,
        "password": password,
        "domain": domain,
        "hostedzoneid": hostedzoneid,
        "sslcertificatearn": sslcertificatearn,
        "natkeypair": natkeypair,
        "pivnettoken": pivnettoken
    })

    print("---------------------------")
    print(rendered)
    print("---------------------------")

    with open('parameters.json', 'w') as rendered_file:
        rendered_file.write(rendered)

    cmd = """
    aws cloudformation create-stack \
              --stack-name pcf-int-`date +%s` \
              --capabilities CAPABILITY_IAM \
              --template-body file:///`pwd`/cloudformation/quickstart-template.yml \
              --parameters file:///`pwd`/parameters.json
 """

    sys.exit(call(cmd, shell=True))
