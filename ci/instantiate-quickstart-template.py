import jinja2

# todo: open ami mapping and templatize that too


with open("templates/quickstart-template.j2.yml", 'r') as f:
    quickstart_template = jinja2.Template(f.read())

with open("cloudformation/quickstart-template-rc.yml", 'w') as template_file:
    rc_context = {
        "quickstart_release_tarball": "quickstart-release-candidate.tgz"
    }
    template_file.write(quickstart_template.render(rc_context))

with open("cloudformation/quickstart-template.yml", 'w') as template_file:
    prod_context = {
        "quickstart_release_tarball": "quickstart-release.tgz"
    }
    template_file.write(quickstart_template.render(prod_context))
