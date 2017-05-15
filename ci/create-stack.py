import jinja2
import os
import sys
from subprocess import call

password = os.environ['AWS_CF_PASSWORD']
domain = os.environ['AWS_CF_DOMAIN']
hostedzoneid = os.environ['AWS_CF_HOSTEDZONEID']
sslcertificatearn = os.environ['AWS_CF_SSLCERTIFICATEARN']
natkeypair = os.environ['AWS_CF_NATKEYPAIR']
pivnettoken = os.environ['AWS_CF_PIVNETTOKEN']

with open('ci/parameters.j2.json', 'r') as template_file:
    template = jinja2.Template(template_file.read())
    ctx = {
        "password": password,
        "domain": domain,
        "hostedzoneid": hostedzoneid,
        "sslcertificatearn": sslcertificatearn,
        "natkeypair": natkeypair,
        "pivnettoken": pivnettoken
    }
    rendered = template.render(ctx)

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
