# Lighthouse to Markdown

This script runs [lighthouse](https://developers.google.com/web/tools/lighthouse/) and provides the result to a primitive markdown templating system.

## Installation

The only dependency at the moment is jinja2. To install, run:

```sh
pip install -r requirements.txt
```

For all help on usage run `python lighthouse2md.py --help`

## Overriding templates

Put custom templates in `./user/templates`, relative to this README
file. This directory will need to be created.

For example, create `./user/templates/index.md` to override the index
template.

The generic audit template is audit_result.md. However, templates for
specific audits can be easily overridden using the audit id. For
example, create ./user/templates/structured-data.md to override the
structured-data audit under SEO/Structured Data.

