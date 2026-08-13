---
title: Third-party plugin compatibility
parent: "Reports"
nav_order: 30
permalink: /products/moodle-report_plugincompatibility/
has_children: true
---

# Third-party plugin compatibility

Third-party plugin compatibility is an administrator report for reviewing installed contributed plugins against a selected Moodle version. It combines local plugin metadata with version information retrieved from moodle.org.

## Requirements and installation

- The current package declares Moodle 3.10 as its minimum and compatibility through Moodle 4.5. Validate newer target releases before production use.
- Install at `report/plugincompat`, complete Moodle's upgrade, and grant `report/plugincompat:view` to authorised managers.
- The Moodle server needs outbound HTTPS access to moodle.org. No API key is required.

## Use and limitations

Select a target Moodle version to see compatible, incompatible, unavailable, and unknown results. Initial loading may be slower while moodle.org data is retrieved; cached version and URL results make later requests faster.

The report supports upgrade planning but cannot guarantee that a third-party plugin is safe or functionally compatible. Review the plugin maintainer's release notes and test the complete upgrade in staging.

## Privacy and external service

The plugin does not store personal data. Requests to moodle.org identify plugin component names and use ordinary server network metadata; they do not intentionally send Moodle user data.

See the [user guide](user.md) for the full administrator workflow.

## Support

- [Report a bug or request a feature](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=product-bug.yml)
- [Pukunui Plugin Subscription Terms & Support Policy](https://pukunui.com/docs/policy-moodle-marketplace/)
- [Pukunui Malaysia](https://pukunui.com/home/location/malaysia/)

Original documentation copyright Pukunui Sdn Bhd and contributors, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---

Source: [moodle-report_plugincompatibility at `1e80e0c48aa0`](https://github.com/PukunuiMalaysia/moodle-report_plugincompatibility/commit/1e80e0c48aa055bbc5b31e483a4e48c8f42103e3). [Report a documentation issue](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=documentation.yml).
