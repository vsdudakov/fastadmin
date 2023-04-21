{% if section_block.type == 'text' %}
{{section_block.content | safe}}
{% endif %}

{% if section_block.type == 'text-lead' %}
{{section_block.content | safe}}
{% endif %}

{% if section_block.type == 'alert-info' %}
{{section_block.content | safe}}
{% endif %}

{% if section_block.type == 'alert-warning' %}
{{section_block.content | safe}}
{% endif %}

{% if section_block.type == 'code-bash' %}
```bash
{{section_block.content | safe}}
```
{% endif %}

{% if section_block.type == 'code-python' %}
```python
{{section_block.content | safe}}
```
{% endif %}

{% if section_block.type == 'tabs' %}
{% for tab in section_block.content %}
### {{tab.name}}
{% for section_block in tab.content %}
{% include "templates/block.md" %}
{% endfor %}

{% endfor %}
{% endif %}
