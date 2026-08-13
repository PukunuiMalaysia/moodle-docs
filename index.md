---
title: Pukunui Moodle documentation
nav_order: 1
---

# Pukunui Moodle documentation

Public user and administrator guidance for Moodle plugins and related tools maintained by Pukunui Malaysia.

{% assign categories = site.data.repositories | group_by: "category" %}
{% for category in categories %}
## {{ category.name }}

{% assign products = category.items | sort: "nav_order" %}
{% for product in products %}
- [{{ product.title }}]({{ site.baseurl }}/products/{{ product.repository }}/)
{% endfor %}
{% endfor %}

Documentation is synchronized from each product repository's `docs/public` directory. Every automated update is reviewed before publication.
