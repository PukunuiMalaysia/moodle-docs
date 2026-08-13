---
title: Completed courses
parent: "Blocks"
nav_order: 10
permalink: /products/moodle-block_completedcourse/
---

# Completed courses

The Completed courses block gives each signed-in user a compact list of their completed Moodle courses. Users can follow course links and, when permitted, export the same visible information as CSV. It never accepts a user ID and cannot be used to browse another user's completion history.

## Requirements and installation

- Moodle 4.5 through 5.2 with course completion enabled for relevant courses.
- Install the plugin at `blocks/completedcourse` through Moodle's normal ZIP installer or filesystem deployment, then complete the Moodle upgrade.
- Add **Completed courses** to a dashboard or another supported block region.

No external service, API credential, Composer, npm, or post-install build is required.

## Configuration

Each block instance can select short or full course names, completion-date order, 1–100 rows per page, a category hierarchy, localised date format, category and grade display, hidden-course handling, and whether course links open in a new tab. Moodle access rules still control whether a hidden course is visible.

The CSV action requires `block/completedcourse:export` and a valid session key. Exported values are protected against spreadsheet formula interpretation.

## Privacy and support

The block stores configuration but no personal data. It reads the current user's Moodle completion and grade records at request time and sends nothing externally.

- [Report a bug or request a feature](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=product-bug.yml)
- [Pukunui Plugin Subscription Terms & Support Policy](https://pukunui.com/docs/policy-moodle-marketplace/)
- [Pukunui Malaysia](https://pukunui.com/home/location/malaysia/)

Original documentation copyright Pukunui Sdn Bhd and contributors, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---

Source: [moodle-block_completedcourse at `cd3fdd9e6b66`](https://github.com/PukunuiMalaysia/moodle-block_completedcourse/commit/cd3fdd9e6b66739cd292c12dc5eacb0cf2d2283e). [Report a documentation issue](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=documentation.yml).
