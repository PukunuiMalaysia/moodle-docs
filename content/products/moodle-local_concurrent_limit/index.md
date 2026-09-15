---
title: Concurrent user limiter
category: Local plugins
nav_order: 10
---

# Concurrent user limiter

Concurrent user limiter provides approximate login admission control using cached recent Moodle session activity. It checks web logins after authentication and newly created webservice tokens. It does not guarantee a strict infrastructure concurrency ceiling.

## Admission behaviour and limitations

The plugin counts each recently active authenticated user once, regardless of the number of their sessions. Each Moodle guest-account session counts separately; anonymous sessions with `userid = 0` are excluded. Session records outside the activity window are ignored without a separate stale-session scan.

Counts are cached for 60 seconds. The admission threshold is `floor(configured limit * 1.05)`: for a configured limit of 100, the threshold is 105. This 5% allowance raises the threshold; it does **not** guarantee a maximum overshoot. There is no atomic reservation of login slots, so many simultaneous logins can pass the same cached check and exceed the threshold by more than 5%.

Existing sessions are not continuously rechecked. The token-creation observer checks only newly created webservice/mobile tokens; requests using existing tokens are not rechecked, and token activity is not counted as simultaneous infrastructure usage. Active-session estimates are not measurements of concurrent HTTP requests, workers, CPU, or memory usage.

When the cached count reaches the threshold, a rejected web login has its current session terminated and is redirected to the public capacity page. A rejected token-creation request deletes the just-created token and returns a capacity error. Existing tokens are retained. Users with `local/concurrent_limit:bypass` are exempt; Moodle's guest account cannot bypass the check. Manager and course creator archetypes have this capability by default.

## Requirements and configuration

The plugin declares support for Moodle 4.5 through 5.2. It uses Moodle's session, cache, lock, task, and mail APIs, with no additional plugin or external-service dependency.

Install an administrator-provided plugin ZIP through **Site administration > Plugins > Install plugins** and complete Moodle notifications. Configure admission control in Moodle's `config.php`:

```php
$CFG->local_concurrent_limit_max = 100;
$CFG->local_concurrent_limit_active_window = 1800;
$CFG->local_concurrent_limit_show_current_users = false;
```

Leaving `local_concurrent_limit_max` unset, or setting a nonpositive value, disables admission control. The active window defaults to 1800 seconds and is capped by a positive Moodle session timeout. The threshold and window are read-only in site administration. Current-user display is disabled by default.

Open **Site administration > Plugins > Local plugins > Concurrent user limiter > Settings** to inspect configuration and set comma-separated alert email recipients. The About page provides installed plugin details, maintainer attribution, and support links.

## Capacity alerts

Rejected admissions can queue an alert through a non-blocking Moodle lock. The hourly throttle is read afresh while holding the lock, and the queue entry and throttle timestamp are saved in one database transaction. Simultaneous rejections therefore admit at most one new alert batch per hour when all web nodes use the same working Moodle lock backend. A request that cannot obtain the lock skips queueing instead of waiting.

Moodle cron delivers alerts in the background, keeping mail transport out of rejected login requests. Configure a shared Moodle lock backend on multi-node sites, run Moodle cron regularly, and configure Moodle's normal outgoing mail settings. The hourly limit applies to queue admission, not delivery times: a delayed queue can deliver batches close together, and retries after a partial mail failure can duplicate messages.

Queued tasks contain only the rejection time, aggregate cached count, and admission threshold. Recipients are read from current plugin configuration when the task runs. Duplicate addresses are removed and invalid addresses are ignored. Clearing recipients cancels delivery from pending tasks. An unsuccessful queue attempt does not intentionally prevent the login or token rejection.

## Privacy and troubleshooting

The plugin reads existing Moodle session records without copying user-session data. Alert addresses are administrator-provided site configuration. Rejections are recorded through Moodle events and managed by Moodle's configured log stores. Background task payloads contain no user identifiers or recipient addresses.

- If admissions exceed the threshold, check the cached-count and existing-token limitations above. The plugin provides approximate admission control.
- If capacity appears stale, check the configured active window and allow for the 60-second count cache. Old records are ignored after they leave the window.
- If alerts are missing, check recipients, cron, the task queue, Moodle's mail configuration, and the shared lock backend. Inspect task failures without exposing mail credentials.
- The capacity page intentionally allows access without login because rejection terminates the session before redirecting there.

## Support and licence

Maintained by Pukunui Malaysia. Licensed under GNU GPL v3 or later.

- [Report a product bug](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=product-bug.yml)
- [Request a feature](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=feature.yml)
- [Contact Pukunui Malaysia](mailto:hello.my@pukunui.com)
- [GNU GPL v3](https://www.gnu.org/licenses/gpl-3.0.html)

Original documentation copyright Pukunui Sdn Bhd and contributors, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
