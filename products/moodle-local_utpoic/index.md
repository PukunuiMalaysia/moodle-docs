---
title: Webservice UTP-OIC
parent: "Local plugins"
nav_order: 60
permalink: /products/moodle-local_utpoic/
---

# Webservice UTP-OIC

Webservice UTP-OIC exposes Moodle user grade-report data through registered external functions for an authorised integration.

## Requirements and installation

- Moodle 3.10 or later as declared by the current package.
- Install at `local/utpoic`, complete Moodle's normal upgrade, enable web services, and create a service token only for a dedicated account with the minimum required capabilities.
- Test the exact Moodle release and mobile or external client in staging before production use.

## Access and data

Requests validate course context and require Moodle grade-report capabilities. Depending on the authorised request, results can include course identifiers, user identifiers and profile fields, grades, feedback, contribution-to-course-total values, and group-filtered report data.

Treat service responses as personal educational records. Use HTTPS, protect tokens, restrict the service account, rotate credentials, and avoid logging response bodies. The plugin does not create its own personal-data store, but the consuming system becomes responsible for any data it retains.

## Support

- [Report a bug or request a feature](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=product-bug.yml)
- [Pukunui Plugin Subscription Terms & Support Policy](https://pukunui.com/docs/policy-moodle-marketplace/)
- [Pukunui Malaysia](https://pukunui.com/home/location/malaysia/)

Original documentation copyright Pukunui Sdn Bhd and contributors, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---

Source: [moodle-local_utpoic at `ded1c6fbafd5`](https://github.com/PukunuiMalaysia/moodle-local_utpoic/commit/ded1c6fbafd5fa39a306e1698906f5664bf480ac). [Report a documentation issue](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=documentation.yml).
