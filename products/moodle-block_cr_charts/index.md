---
title: Configurable reports chart
parent: "Blocks"
nav_order: 30
permalink: /products/moodle-block_cr_charts/
---

# Configurable reports chart

Configurable reports chart turns SQL report results from the Configurable Reports block into Moodle core charts. Each block instance selects a report, chart type, label column, and numeric value column.

## Requirements and installation

- Moodle 4.5 or later.
- The Configurable Reports block must be installed; Moodle declares it as a plugin dependency.
- Install at `blocks/cr_charts`, complete the Moodle upgrade, then add and configure the block on a dashboard or course page.

## Configuration and behaviour

Choose a visible Configurable Reports SQL report and enter the exact result aliases to use for labels and numeric values. The block supports multiple instances, standard Configurable Reports placeholders, date filters, and Moodle's accessible Chart API. Empty results or missing configured aliases produce a Moodle notification instead of exposing SQL errors.

The block stores instance configuration and cached chart results. Report SQL is administrator-controlled and may return personal information; access to both the source report and the page containing the chart should be limited accordingly.

## Support

- [Report a bug or request a feature](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=product-bug.yml)
- [Pukunui Plugin Subscription Terms & Support Policy](https://pukunui.com/docs/policy-moodle-marketplace/)
- [Pukunui Malaysia](https://pukunui.com/home/location/malaysia/)

Original documentation copyright Pukunui Sdn Bhd and contributors, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---

Source: [moodle-block_cr_charts at `0f5dacfb4783`](https://github.com/PukunuiMalaysia/moodle-block_cr_charts/commit/0f5dacfb47838193325568b72fcf7ca3ca5dc44c). [Report a documentation issue](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=documentation.yml).
