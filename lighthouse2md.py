from __future__ import print_function
import argparse
import jinja2
import os
import json
import sys



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
parser.add_argument("-i", "--input-file", help="Provide athe path to an input file", default=sys.stdin)
parser.add_argument("-o", "--output-file", help='Provide a filepath where the markdown result gets written')
parser.add_argument("-e", action='store_true', default=False,
                    help='Echo the output to stdout, even when using the -o option')
args = parser.parse_args()

if type(args.input_file) is str:
    with open(args.input_file) as stream:
        data = json.JSONDecoder().decode(stream.read())
else:
    data = json.JSONDecoder().decode(args.input_file.read())

for cat in data['categories']:
    data['categories'][cat]['audits'] = dict()
    for audit_ref in data['categories'][cat]['auditRefs']:
        audit = data['audits'][audit_ref['id']]
        audit['audit_template'] = '%s.md' % audit_ref['id']
        if 'displayValue' in audit and type(audit['displayValue']) is list:
            try:
                audit['displayValue'] = audit['displayValue'][0] % tuple(audit['displayValue'][1:])
            except TypeError:
                print(audit)
        data['categories'][cat]['audits'][audit_ref['id']] = audit

loader = jinja2.FileSystemLoader([
    os.path.join(SCRIPT_PATH, 'user', 'templates'),
    os.path.join(SCRIPT_PATH, 'templates')
])

env = jinja2.Environment(loader=loader)


template = loader.load(env, 'index.md')
rendered = template.render({'data': data})

if args.output_file:
    with open(args.output_file, 'w') as stream:
        stream.write(rendered.encode('utf-8'))

    if args.e:
        print(rendered)
else:
    print(rendered)
