---
title: Completion points view
parent: "Blocks"
nav_order: 20
permalink: /products/moodle-block_completionpoints_view/
---

# Completion points view

Completion points view is a block that displays a user's completion point records for the current calendar year. It reads records owned by the Course completion points local plugin and shows the course, points, notes, date, and yearly total.

## Requirements and installation

- Moodle 4.1 or later.
- `local_completionpoints` version `2023092501` or later must be installed first.
- Install this plugin at `blocks/completionpoints_view`, complete the Moodle upgrade, and add the block to a supported page.

No external service, credentials, or post-install build tools are required.

## Access and privacy

The current signed-in user's records are shown by default. A site administrator may inspect another user by using Moodle's supported user-ID route; non-administrators cannot use that override.

This block does not store personal data itself. The required `local_completionpoints` plugin owns the point records and its Privacy API provider governs their export and deletion.

## Support

- [Report a bug or request a feature](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=product-bug.yml)
- [Pukunui Plugin Subscription Terms & Support Policy](https://pukunui.com/docs/policy-moodle-marketplace/)
- [Pukunui Malaysia](https://pukunui.com/home/location/malaysia/)

Original documentation copyright Pukunui Sdn Bhd and contributors, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---

Source: [moodle-block_completionpoints_view at `48ef729390b4`](https://github.com/PukunuiMalaysia/moodle-block_completionpoints_view/commit/48ef729390b44ccfe7edbb14561ec8e445812de4). [Report a documentation issue](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=documentation.yml).
