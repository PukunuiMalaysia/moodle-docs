---
title: Image optimizer
parent: "Local plugins"
nav_order: 50
permalink: /products/moodle-local_imageopt/
---

# Image optimizer

Image optimizer safely batch-optimizes eligible images stored through Moodle's File API. It provides administrator settings and reporting, an hourly scheduled task, and controlled CLI scans while keeping Moodle file references stable.

## Requirements and installation

- Moodle 5.1 or 5.2 on the active `main` branch.
- Install at `local/imageopt`, complete the Moodle upgrade, and configure it under **Site administration > Plugins > Local plugins > Image optimizer**.
- Moodle cron must run for scheduled processing.

Moodle 4.5 is frozen at release `v0.1.1` and receives no further updates.

## Safety defaults

New installations are disabled and use dry-run mode. Scheduled runs default to at most 50 files or five minutes. Review dry-run results before enabling writes. The plugin excludes transient drafts and known generated or sensitive areas, isolates failures, prevents overlapping runs through Moodle's Lock API, and avoids reprocessing unchanged results.

Only Moodle administrators should access reports and manual runs. Reports and logs use bounded counters and should not expose filenames, paths, URLs, or image content.

## Privacy

The plugin processes Moodle files in place and stores optimization statistics. It does not send files to an external service. Administrators should still review eligible file areas and retention expectations because user-uploaded images may contain personal data.

## Support

- [Report a bug or request a feature](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=product-bug.yml)
- [Pukunui Plugin Subscription Terms & Support Policy](https://pukunui.com/docs/policy-moodle-marketplace/)
- [Pukunui Malaysia](https://pukunui.com/home/location/malaysia/)

Original documentation copyright Pukunui Sdn Bhd and contributors, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---

Source: [moodle-local_imageopt at `8143c7606390`](https://github.com/PukunuiMalaysia/moodle-local_imageopt/commit/8143c760639066a0cd15b65fb276668964c9f470). [Report a documentation issue](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=documentation.yml).
