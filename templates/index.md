# Report

{% for cat in data.reportCategories %}
## {{ cat.name }}
{% for audit in cat.audits %}
### {{ audit.result.description }}

{% include [audit.audit_template, "audit_result.md"] %}
{% endfor %}
{%- endfor -%}
