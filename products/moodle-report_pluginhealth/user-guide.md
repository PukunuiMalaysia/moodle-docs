---
title: Plugin health user guide
parent: "Plugin health report"
grand_parent: "Reports"
---

# Plugin health user guide

Open **Site administration > Reports > Plugin health**, select a current-or-newer Moodle target, and choose **Analyse plugin health**. Local inventory appears immediately; declared Marketplace evidence is then loaded in small batches.

Use the summary, search and filters to review:

- **Ready:** installed code declares target support and required dependencies pass.
- **Update required:** a higher target-compatible release is available.
- **Blocked:** local state or a dependency is invalid, or a listed plugin has no target release.
- **Manual review:** local and remote evidence conflicts, or custom/unlisted code is inconclusive.
- **Unknown:** remote evidence is unavailable and installed code is inconclusive.

Prioritise blockers with active aggregate usage or many dependent plugins. CSV and JSON downloads contain the complete target report and omit package download URLs.

These results describe metadata, not runtime test results. Install candidate releases and complete regression testing in staging before upgrading production.

For help, use [Pukunui Malaysia support and bug reporting](https://pukunui.com/home/location/malaysia/). The [Pukunui Plugin Subscription Terms & Support Policy](https://pukunui.com/docs/policy-moodle-marketplace/) also applies.
