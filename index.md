---
title: Pukunui Moodle documentation
nav_order: 1
has_toc: false
---

<div class="pukunui-hero">
  <p class="pukunui-eyebrow">Pukunui Moodle products</p>
  <h1>Documentation that helps you get more from Moodle.</h1>
  <p class="pukunui-lead">Clear guidance for installing, configuring, and using Moodle plugins and related tools maintained by Pukunui Malaysia.</p>
  <div class="pukunui-actions">
    <a class="btn btn-primary" href="#browse-products">Browse documentation</a>
    <a class="btn btn-outline" href="https://github.com/PukunuiMalaysia/moodle-docs/issues/new/choose">Ask for help</a>
  </div>
</div>

<h2 id="browse-products">Browse products</h2>

<div class="pukunui-category-grid">
{% assign categories = site.data.repositories | group_by: "category" %}
{% for category in categories %}
  <section class="pukunui-category-card">
    <h3>{{ category.name }}</h3>
    <ul>
    {% assign products = category.items | sort: "nav_order" %}
    {% for product in products %}
      <li><a href="{{ '/products/' | append: product.repository | append: '/' | relative_url }}">{{ product.title }}</a></li>
    {% endfor %}
    </ul>
  </section>
{% endfor %}
</div>

<div class="pukunui-callout">
  <strong>Reviewed before publication.</strong>
  <p>Documentation is synchronized from each product repository's <code>docs/public</code> directory. Automated updates are published only after review.</p>
</div>
