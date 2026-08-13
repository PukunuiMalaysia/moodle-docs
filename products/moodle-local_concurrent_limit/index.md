---
title: Concurrent user limiter
parent: "Local plugins"
nav_order: 30
permalink: /products/moodle-local_concurrent_limit/
---

# Concurrent user limiter

Concurrent user limiter enforces a site-wide threshold based on recently active Moodle sessions. It includes a 5% soft buffer for short cache races, a bypass capability, throttled capacity alerts, and handling for web and mobile logins.

## Requirements and installation

- Moodle 4.0 or later.
- Install at `local/concurrent_limit` and complete Moodle's standard upgrade.
- Leave the limit unset during setup. Enforcement remains disabled until a server administrator adds it to `config.php`.

```php
$CFG->local_concurrent_limit_max = 100;
$CFG->local_concurrent_limit_active_window = 1800;
$CFG->local_concurrent_limit_show_current_users = false;
```

Alert recipients are configured under **Site administration > Plugins > Local plugins > Concurrent user limiter**. The enforced limit is deliberately not editable in Moodle administration.

## Behaviour and privacy

The limiter counts distinct recently active authenticated users, counts guest-account sessions separately, and ignores anonymous records. The effective threshold is `floor(configured limit * 1.05)`. Users with `local/concurrent_limit:bypass` are exempt except for the guest account.

The plugin reads Moodle session records and stores cache and event information required for enforcement. Current counts are hidden in the administrator interface unless explicitly enabled. No data is sent externally.

## Support

- [Report a bug or request a feature](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=product-bug.yml)
- [Pukunui Plugin Subscription Terms & Support Policy](https://pukunui.com/docs/policy-moodle-marketplace/)
- [Pukunui Malaysia](https://pukunui.com/home/location/malaysia/)

Original documentation copyright Pukunui Sdn Bhd and contributors, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---

Source: [moodle-local_concurrent_limit at `4c7ca95514d0`](https://github.com/PukunuiMalaysia/moodle-local_concurrent_limit/commit/4c7ca95514d0a544dab17618bd9852863f04d3c2). [Report a documentation issue](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=documentation.yml).
