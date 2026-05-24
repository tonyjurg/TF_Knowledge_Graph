---
layout: default
title: TF Knowledge Graph
---

{% capture readme_content %}
{% include_relative README.md %}
{% endcapture %}

{{ readme_content | markdownify }}
