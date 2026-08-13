---
title: Course completion points
parent: "Local plugins"
nav_order: 20
permalink: /products/moodle-local_completionpoints/
---

# Course completion points

Course completion points records points against a user when Moodle reports course completion. Administrators can configure defaults, review records, add or edit entries, and import entries from CSV.

## Requirements and installation

- Moodle 4.1 or later.
- Install at `local/completionpoints`, complete Moodle's standard upgrade, then enable the plugin under **Site administration > Plugins > Local plugins > Course completion points**.
- The optional Completion points view block can display these records. Install this local plugin before the block.

## Configuration and use

Configure whether automatic recording is enabled, the default points, and default notes. The plugin observes Moodle's course-completed event and records the course, user, points, notes, and timestamps.

CSV imports use the columns `username,course_shortname,points,notes`. Validate import data in a non-production environment before a large import.

## Privacy

The plugin stores user ID, course ID, awarded points, notes, and created and modified timestamps in Moodle. It sends no data to external services and declares the stored data through Moodle's Privacy API.

## Support

- [Report a bug or request a feature](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=product-bug.yml)
- [Pukunui Plugin Subscription Terms & Support Policy](https://pukunui.com/docs/policy-moodle-marketplace/)
- [Pukunui Malaysia](https://pukunui.com/home/location/malaysia/)

Original documentation copyright Pukunui Sdn Bhd and contributors, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---

Source: [moodle-local_completionpoints at `a8c109953458`](https://github.com/PukunuiMalaysia/moodle-local_completionpoints/commit/a8c109953458bcb92a7481ac975dd85d15801d89). [Report a documentation issue](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=documentation.yml).
