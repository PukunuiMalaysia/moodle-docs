---
title: ASEC LMS report
parent: "Reports"
nav_order: 10
permalink: /products/moodle-report_asec/
---

# ASEC LMS report

ASEC LMS report provides authorised managers with four Moodle reporting views: module access, learner progress, learning result, and module feedback score.

## Requirements and installation

- Moodle 5.0 through 5.2.
- Install at `report/asec`, complete Moodle's standard upgrade, and grant `report/asec:view` only to roles that should access learning records.
- The Standard logstore is required for module-access counts. Pre-test, Post-test, and Module feedback activities must be named and configured consistently in each course.

## Use

Module, category, and compulsory filters apply across all tabs and exports. Learning results use the configured Post-test pass mark. Missing grades are **In progress**; invalid mappings or missing pass marks are **Unavailable**. Module feedback uses the first three rated multiple-choice items for relevancy, impact, and quality.

Excel downloads contain the filtered table only and protect formula-like text. Review capabilities and the export audience before distributing files.

## Privacy

The report reads learner progress, grades, feedback, course access events, and profile information from Moodle. It does not create a separate personal-data store or send records externally. Access requires the report capability at system context.

## Support

- [Report a bug or request a feature](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=product-bug.yml)
- [Pukunui Plugin Subscription Terms & Support Policy](https://pukunui.com/docs/policy-moodle-marketplace/)
- [Pukunui Malaysia](https://pukunui.com/home/location/malaysia/)

Original documentation copyright Pukunui Sdn Bhd and contributors, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---

Source: [moodle-report_asec at `75831dba099c`](https://github.com/PukunuiMalaysia/moodle-report_asec/commit/75831dba099cca9010b6548e4bf6dc451db9d866). [Report a documentation issue](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=documentation.yml).
