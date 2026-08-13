---
title: HRD Corp attendance report
parent: "Reports"
nav_order: 20
permalink: /products/moodle-report_hrdc/
---

# HRD Corp attendance report

HRD Corp attendance report helps site administrators prepare a printable attendance record from Moodle core data for self-paced e-learning and live remote training runs. It is supporting evidence, not an official HRD Corp form, legal opinion, eligibility decision, or eTRiS integration.

## Requirements and installation

- Moodle 4.5 through 5.2 with Standard logstore enabled.
- Install at `report/hrdc`, complete the Moodle upgrade, and configure provider details and participant-field mappings.
- Version 0.1 is restricted to site administrators and requires `moodle/site:config` plus the relevant plugin capability.

## Workflow

Create a training run for a course, group, and employer; select participant roles; add non-overlapping scheduled windows; then review each date and record each participant as **Present**, **Absent**, or **Pending**. Evidence-free present decisions require a reason. Resolve readiness errors before printing or saving the browser view as PDF.

Activity spans are supporting Moodle evidence and may include idle time. Administrators remain responsible for participant data, declarations, signatures, stamps, dates, and current HRD Corp rules.

## Privacy

The plugin stores attendance decisions, reasons, actor references, training-run configuration, and optional signatory details. It reads participant profiles and Standard logstore events. Moodle's Privacy API exports participant and decision-maker records and supports deletion or anonymisation. No data is sent externally.

## Support

- [Report a bug or request a feature](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=product-bug.yml)
- [Pukunui Plugin Subscription Terms & Support Policy](https://pukunui.com/docs/policy-moodle-marketplace/)
- [Pukunui Malaysia](https://pukunui.com/home/location/malaysia/)

Original documentation copyright Pukunui Sdn Bhd and contributors, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---

Source: [moodle-report_hrdc at `8869afea46c5`](https://github.com/PukunuiMalaysia/moodle-report_hrdc/commit/8869afea46c53083d94c35b52eaebff647816b76). [Report a documentation issue](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=documentation.yml).
