from __future__ import print_function
import argparse
import jinja2
import os
import json
import sys


SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))


def get_args():
    example_text = '''
    examples:
    
    %(lighthouse)s -i /tmp/google.com.json -o /tmp/google.com.md -e
       
    ''' % {'lighthouse': os.path.basename(__file__)}

    parser = argparse.ArgumentParser(epilog=example_text, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-i", "--input-file", help="Provide athe path to an input file", default=sys.stdin)
    parser.add_argument("-o", "--output-file", help='Provide a filepath where the markdown result gets written')
    parser.add_argument("-e", action='store_true', default=False,
                        help='Echo the output to stdout, even when using the -o option')
    return parser.parse_args()


def preprocess_data(data):
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
    return data


def read_input(input_file):
    if type(input_file) is str:
        with open(input_file) as stream:
            return json.JSONDecoder().decode(stream.read())
    else:
        return json.JSONDecoder().decode(args.input_file.read())


def main():
    args = get_args()

    loader = jinja2.FileSystemLoader([
        os.path.join(SCRIPT_PATH, 'user', 'templates'),
        os.path.join(SCRIPT_PATH, 'templates')
    ])

    env = jinja2.Environment(loader=loader)

    template = loader.load(env, 'index.md')
    rendered = template.render({
        'data': preprocess_data(read_input(args.input_file))
    })

    if args.output_file:
        with open(args.output_file, 'w') as stream:
            stream.write(rendered.encode('utf-8'))

        if args.e:
            print(rendered)
    else:
        print(rendered)


if __name__ == '__main__':
    main()
