import json
import os
import re
import sys

import jinja2
import yaml

versioned_file_name = ""
ami_mapping_dir = "../ami-mapping"

for file_name in os.listdir(ami_mapping_dir):
    if re.match(r'ami-mapping-.*\.json', file_name):
        versioned_file_name = file_name

if versioned_file_name == "":
    print("Unable to find ami-mapping file")
    sys.exit(1)

with open(os.path.join(ami_mapping_dir, versioned_file_name)) as f:
    raw_mapping = json.load(f)
    mapping = {}
    for key in raw_mapping:
        mapping[key] = {"64": raw_mapping[key]}

mapping_yaml = yaml.dump(mapping, default_flow_style=False)

with open("templates/quickstart-template.j2.yml", 'r') as f:
    quickstart_template = jinja2.Template(f.read())

context = {
    "bootstrap_ami_mapping": mapping_yaml
}

with open("cloudformation/quickstart-template-rc.yml", 'w') as template_file:
    template_file.write(quickstart_template.render(context))
