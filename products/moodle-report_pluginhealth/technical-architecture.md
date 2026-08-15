---
title: Plugin health technical architecture
parent: "Plugin health report"
grand_parent: "Reports"
---

# Plugin health technical architecture

## Component

- Frankenstyle: `report_pluginhealth`
- Install path: `report/pluginhealth`
- Capability: `report/pluginhealth:view`
- Supported Moodle branches: 4.5–5.2

The component is a new plugin identity. It has no database schema or upgrade migration from the former experimental project.

## Data flow

1. The report page collects contributed plugins through `core_plugin_manager` and renders local inventory immediately.
2. The AMD module requests batches through `report_pluginhealth_get_readiness_batch`.
3. The scanner requests exact-version and target-branch metadata through the Marketplace client.
4. The analyser combines local declarations, local dependencies, Marketplace evidence and aggregate usage.
5. Results are returned without package URLs and rendered using DOM text nodes and validated HTTP(S) links.

## Marketplace client

The client calls `https://download.moodle.org/api/1.3/pluginfo.php`, matching Moodle core's plugin metadata contract. It uses Moodle's proxy-aware `curl` wrapper with peer and host verification enabled.

Outcomes are explicit:

- found;
- listed without a suitable release;
- not found;
- rate limited;
- transport error; and
- invalid response.

Successful and not-found results are cached for 24 hours. Transient failures are cached for five minutes. Cached payloads contain only the public fields used by the report; download URLs and hashes are discarded.

## Readiness rules

Local `requires`, `supported` and `incompatible` declarations describe installed code and take precedence. Exact Marketplace release metadata fills gaps when local support is inconclusive. Contradictions require manual review.

A plugin is blocked before remote analysis when its Moodle plugin state is not up to date, a declared dependency is missing or outdated, or a dependency explicitly rejects the target branch.

No numeric health score is calculated. State, evidence, usage and dependency fan-in remain separate so administrators can make defensible decisions.

## Security and privacy

- System context and `report/pluginhealth:view` are required for the page, AJAX endpoint and exports.
- Target releases come from a fixed allowlist.
- Plugin discovery is server-side; clients cannot submit arbitrary components for lookup.
- Remote errors are reduced to safe state descriptions rather than raw stack traces.
- Output is escaped through Mustache or DOM text nodes; provider links must use HTTP(S).
- The plugin stores no personal data and only reads aggregate usage counts.

Component names, installed versions and selected targets are sent to Moodle's public metadata service as declared by the Privacy API.

## Testing

Automated tests use injected transport responses and cached fixtures, not live Marketplace requests. A separate manual smoke test should cover one free listing, one paid listing and one unlisted component.

For support, see [Pukunui Malaysia](https://pukunui.com/home/location/malaysia/) and the [Pukunui Plugin Subscription Terms & Support Policy](https://pukunui.com/docs/policy-moodle-marketplace/).
