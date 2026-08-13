---
title: Activity Groups Format
parent: "Course formats"
nav_order: 10
permalink: /products/moodle-format_activitygroups/
---

# Activity Groups Format

Activity Groups Format groups visible course activities and resources into administrator-defined display areas based on Moodle module type. It changes presentation only: it does not create, duplicate, move, or delete course modules.

## Requirements and installation

- Moodle 4.5 or later.
- Install at `course/format/activitygroups` and complete Moodle's standard upgrade.
- Select **Activity Groups Format** in a course's settings.

## Configuration

Under **Site administration > Plugins > Course formats > Activity Groups Format**, administrators can configure up to six enabled groups, each with a title and comma-separated Moodle module names. Unmapped modules appear in the fallback group.

Editing mode retains Moodle's standard activity controls so teachers can add, update, hide, show, and delete activities. Group placement is controlled by the module-type mapping rather than drag and drop.

The format stores course settings but no personal data and declares a null Privacy API provider.

## Support

- [Report a bug or request a feature](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=product-bug.yml)
- [Pukunui Plugin Subscription Terms & Support Policy](https://pukunui.com/docs/policy-moodle-marketplace/)
- [Pukunui Malaysia](https://pukunui.com/home/location/malaysia/)

Original documentation copyright Pukunui Sdn Bhd and contributors, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---

Source: [moodle-format_activitygroups at `ada2460d0b91`](https://github.com/PukunuiMalaysia/moodle-format_activitygroups/commit/ada2460d0b916c1e531fc5e850984db148b141f0). [Report a documentation issue](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=documentation.yml).
