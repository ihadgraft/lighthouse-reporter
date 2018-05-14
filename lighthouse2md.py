from __future__ import print_function
import argparse
from subprocess import Popen, PIPE
import jinja2
import re
import os
from datetime import datetime
import json


SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

example_text = '''
examples:

%(lighthouse)s -u https://google.com -o /tmp/google.com.md -e

%(lighthouse)s -u https://google.com -l /home/foo/.local/bin/lighthouse
   Run lighthouse from /home/foo/.local/bin
   
%(lighthouse)s -u https://google.com -- --config-path=/path/to/config.js
   Use a custom config file, and/or pass any other supported options to lighthouse
   
''' % {'lighthouse': os.path.basename(__file__)}

parser = argparse.ArgumentParser(epilog=example_text, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("extra_arguments", nargs='*',
                    help="Additional arguments to lighthouse. The first argument should be --")
parser.add_argument("-u", "--url", required=True, help='The URL to run lighthouse on')
parser.add_argument("-o", "--output-file", help='Provide a filepath where the markdown result gets written')
parser.add_argument("-l", "--lighthouse-bin", default='lighthouse',
                    help='Specify explicit path to the lighthouse binary')
parser.add_argument("-e", action='store_true', default=False,
                    help='Echo the output to stdout, even when using the -o option')
args = parser.parse_args()


class LighthouseException(Exception):
    pass


if not os.path.exists(os.path.join(SCRIPT_PATH, 'cache')):
    os.mkdir(os.path.join(SCRIPT_PATH, 'cache'))

cache_filename = '%s.json' % re.sub('^https?://', '', args.url)
cache_path = '%s/cache/%s' % (SCRIPT_PATH, cache_filename)

if os.path.exists(cache_path) and (os.path.getmtime(cache_path) + 3600) > datetime.now().timestamp():
    with open(cache_path) as stream:
        raw = stream.read()
else:
    popen_args = [args.lighthouse_bin, '--output=json']
    if args.extra_arguments:
        popen_args.extend(args.extra_arguments)
    popen_args.append(args.url)

    proc = Popen(popen_args, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()
    if proc.returncode == 0:
        raw = out.decode('utf-8')
        with open(cache_path, 'w') as stream:
            stream.write(raw)
    else:
        raise LighthouseException(err.decode())


data = json.JSONDecoder().decode(raw)

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
