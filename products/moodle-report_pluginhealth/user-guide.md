---
title: Plugin health user guide
parent: "Plugin health report"
grand_parent: "Reports"
---

# Plugin health user guide

## Purpose

Plugin health helps administrators turn third-party plugin metadata into an upgrade action list. It does not claim that a plugin has been functionally tested on the target Moodle release.

## Run an analysis

1. Open **Site administration > Reports > Plugin health**.
2. Choose a target Moodle version. Targets older than the running site are not offered.
3. Select **Analyse plugin health**.
4. Leave the page open while plugin batches are checked. Local inventory is displayed before remote requests begin.

The summary counts and table update progressively. Filters can narrow results by state, plugin type, enabled state or Marketplace listing.

## Understand the results

- **Ready:** installed code declares target support and required dependencies pass.
- **Update required:** a higher target-compatible release is available.
- **Blocked:** local state or a dependency is invalid, or a listed plugin has no target release.
- **Manual review:** local and remote evidence conflicts, or custom/unlisted code is inconclusive.
- **Unknown:** remote evidence is unavailable and local declarations are inconclusive.

An unlisted plugin can be Ready when its installed `version.php` explicitly declares target support. The result remains marked as local-only because Marketplace metadata is unavailable.

## Prioritise work

Start with Blocked and Manual review results that have active usage or are required by other plugins. Continue with Update required results. Ready results still require staging and regression testing.

The impact count is deliberately limited to non-personal aggregate records:

- activity instances;
- block instances;
- questions by question type;
- courses by course format; and
- enrolment method instances.

For other plugin types, the report displays enabled state and dependency information without guessing a usage score.

## Exports

CSV and JSON downloads become available after the on-screen analysis completes. They contain the full report for the selected target, not only currently visible filtered rows.

Exports omit package download URLs. This report does not install plugins or determine whether a Marketplace purchase is required.

## Troubleshooting

- **Unknown:** retry later and verify Moodle's proxy/outbound HTTPS configuration.
- **Manual review:** inspect the installed plugin's source and release documentation, then run it in staging.
- **Local-only:** the installed code declares target support, but the component is not listed in Marketplace.
- **Conflicting evidence:** treat installed code and Marketplace metadata as unresolved until the maintainer confirms the intended release.

For help, use [Pukunui Malaysia support and bug reporting](https://pukunui.com/home/location/malaysia/). The [Pukunui Plugin Subscription Terms & Support Policy](https://pukunui.com/docs/policy-moodle-marketplace/) also applies.
