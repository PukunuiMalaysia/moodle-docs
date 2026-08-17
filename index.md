---
title: Pukunui Moodle documentation
nav_order: 1
has_toc: false
---

<div class="pukunui-hero">
  <p class="pukunui-eyebrow">Pukunui product documentation</p>
  <h1>Practical guidance for your learning platform.</h1>
  <p class="pukunui-lead">Installation, configuration, administration, and usage guidance for supported LMS products and related tools maintained by Pukunui Malaysia.</p>
  <div class="pukunui-actions">
    <a class="btn btn-primary" href="#browse-products">Browse documentation</a>
    <a class="btn btn-outline" href="https://github.com/PukunuiMalaysia/moodle-docs/issues/new/choose">Ask for help</a>
  </div>
</div>

## About this documentation

This site is the public documentation hub for Pukunui-maintained learning-platform software, including products compatible with Moodle™. It is designed for LMS administrators, educators, support teams, and technical implementers who need clear guidance for deploying and using these products.

Each guide is organised by product and may cover installation, configuration, permissions, supported versions, day-to-day use, and troubleshooting.

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
  <strong>Maintained and reviewed.</strong>
  <p>Documentation is maintained alongside each product and reviewed before it appears on this public site.</p>
</div>
