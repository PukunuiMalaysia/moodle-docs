---
title: Plugin health technical architecture
parent: "Plugin health report"
grand_parent: "Reports"
---

# Plugin health technical architecture

Plugin health is component `report_pluginhealth`, installed at `report/pluginhealth`, and supports Moodle 4.5 through 5.2. Access is controlled by `report/pluginhealth:view` in system context.

Moodle's plugin manager provides installed/database versions, state, requirements, supported and incompatible ranges, dependencies and reverse dependencies. Aggregate queries count activities, blocks, question types, course formats and enrolment methods without reading personal records.

The report calls Moodle's official `https://download.moodle.org/api/1.3/pluginfo.php` contract through Moodle's proxy-aware `curl` wrapper with TLS peer and host verification. Exact-release and target-branch results distinguish found, listed without a release, unlisted, rate-limited, transport-error and invalid-response outcomes. Successful and unlisted results are cached for 24 hours; transient failures for five minutes.

An AJAX-only external function, `report_pluginhealth_get_readiness_batch`, progressively returns capability-protected batches. CSV and JSON exports re-use the same readiness engine, omit package URLs, and neutralise spreadsheet formula prefixes in CSV values.

The plugin stores no personal data. Component names, installed versions and selected targets are sent to Moodle's public metadata service as declared by the Privacy API.

For support, see [Pukunui Malaysia](https://pukunui.com/home/location/malaysia/) and the [Pukunui Plugin Subscription Terms & Support Policy](https://pukunui.com/docs/policy-moodle-marketplace/).
