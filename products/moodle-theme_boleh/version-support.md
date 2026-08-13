---
title: Moodle version support
parent: "Boleh"
grand_parent: "Themes"
---

# Moodle version support

Boleh uses `main` for Moodle 5.0 onwards. Moodle 4.5 LTS is maintained on the
locked `MOODLE_405_STABLE` branch, which accepts bug fixes and security fixes
only.

## Supported releases

| Plugin branch | Moodle | Core branch | PHP in CI | Database in CI | Status |
| --- | --- | --- | --- | --- | --- |
| `main` | 5.0 | `MOODLE_500_STABLE` | 8.3 | PostgreSQL | Active |
| `main` | 5.1 | `MOODLE_501_STABLE` | 8.3 | PostgreSQL | Active |
| `main` | 5.2 | `MOODLE_502_STABLE` | 8.3 | PostgreSQL | Active |
| `MOODLE_405_STABLE` | 4.5 LTS | `MOODLE_405_STABLE` | 8.3 | PostgreSQL | Bug fixes only |

The `main` branch contract is also declared in `version.php` as
`$plugin->supported = [500, 502]`.

## Compatibility rules

- Use Moodle APIs available throughout the Moodle 5.0 to 5.2 supported range.
- Keep new features on `main`; backport only bug fixes and security fixes to
  `MOODLE_405_STABLE`.
- Inherit Boost layouts when Boleh does not need a custom layout.
- Keep custom renderer and template overrides minimal.
- Use `boleh-` component classes instead of Bootstrap classes removed between
  Moodle versions.
- Test guest, login, dashboard, course, activity, and administration layouts
  with developer debugging enabled.
- Treat a missing fixed navbar, primary navigation, user menu, drawer control,
  or edit switch as a release blocker.

## Release gates

Every pull request and push to `main` runs the Moodle 5.0, 5.1, and 5.2 GitHub
Actions matrix. Each matrix job must pass:

1. PHP lint.
2. Moodle coding standards with zero warnings.
3. Moodle PHPDoc checks with zero warnings.
4. Plugin validation and upgrade savepoint checks.
5. Mustache lint.
6. Grunt lint/build checks.
7. PHPUnit.
8. The Boleh Behat regression, including authenticated navbar checks.

Before a tagged release, repeat the matrix against clean Moodle installations
with developer debugging enabled and visually inspect desktop and mobile pages.
Run an installation or upgrade test on both MySQL and PostgreSQL before
Marketplace submission.
