---
title: Credential Lifecycle Manager
parent: "Local plugins"
nav_order: 10
permalink: /products/moodle-local_clm/
---

# Credential Lifecycle Manager

Credential Lifecycle Manager manages credential issue, expiry, renewal, evidence, approval, verification, audit history, and retention inside Moodle.

## Requirements and installation

- Moodle 4.5 LTS.
- Install the repository's `local/clm` directory at `local/clm`, then complete the Moodle upgrade.
- Configure warning days, renewal and grace periods, retention mode, dry-run behaviour, and the required role capabilities.

No external service, Composer, npm, or post-install build is required. External licensing and HRIS integrations are not part of the current release.

## Administration

Administrators create credential rules mapped to Moodle courses and choose a duration, annual date, or fixed expiry. Course completion can issue or renew credentials. Learners can upload offline evidence through Moodle's File API, and authorised reviewers can approve or reject it. Scheduled and ad-hoc tasks handle reminders, expiry processing, and imports; Moodle cron must run regularly.

Optional public verification exposes only the credential or course, issue date, expiry date, and status. It does not display email addresses, usernames, user IDs, or private profile fields.

## Privacy and retention

The plugin stores credential history, evidence metadata and files, and notification logs. Moodle's Privacy API supports export and deletion. Administrators can retain identifiable records, anonymise expired records after a legal-hold period, or delete non-audit data. Destructive lifecycle operations are dry-run by default and should be tested before being enabled.

## Support

- [Report a bug or request a feature](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=product-bug.yml)
- [Pukunui Plugin Subscription Terms & Support Policy](https://pukunui.com/docs/policy-moodle-marketplace/)
- [Pukunui Malaysia](https://pukunui.com/home/location/malaysia/)

Original documentation copyright Pukunui Sdn Bhd and contributors, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---

Source: [moodle-local_clm at `1f3b704f108a`](https://github.com/PukunuiMalaysia/moodle-local_clm/commit/1f3b704f108a308d428fc2f5811f5483141e8ca6). [Report a documentation issue](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=documentation.yml).
