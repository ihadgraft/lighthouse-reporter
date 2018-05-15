from __future__ import print_function
import argparse
import jinja2
import os
import json


SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

example_text = '''
examples:

%(lighthouse)s -i /tmp/google.com.json -o /tmp/google.com.md -e

%(lighthouse)s -u https://google.com -l /home/foo/.local/bin/lighthouse
   Run lighthouse from /home/foo/.local/bin
   
%(lighthouse)s -u https://google.com -- --config-path=/path/to/config.js
   Use a custom config file, and/or pass any other supported options to lighthouse
   
''' % {'lighthouse': os.path.basename(__file__)}

parser = argparse.ArgumentParser(epilog=example_text, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-i", "--input-file", help="Provide athe path to an input file")
parser.add_argument("-o", "--output-file", help='Provide a filepath where the markdown result gets written')
parser.add_argument("-e", action='store_true', default=False,
                    help='Echo the output to stdout, even when using the -o option')
args = parser.parse_args()

with open(args.input_file) as stream:
    data = json.JSONDecoder().decode(stream.read())

for cat in data['reportCategories']:
    for audit in cat['audits']:
        audit['full_audit'] = data['audits'][audit['id']]
        audit['audit_template'] = '%s.md' % audit['id']

loader = jinja2.FileSystemLoader([
    os.path.join(SCRIPT_PATH, 'user', 'templates'),
    os.path.join(SCRIPT_PATH, 'templates')
])

env = jinja2.Environment(loader=loader)


template = loader.load(env, 'index.md')
rendered = template.render({'data': data})

if args.output_file:
    with open(args.output_file, 'w') as stream:
        stream.write(rendered)

    if args.e:
        print(rendered)
else:
    print(rendered)
