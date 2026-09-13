---
title: Completion points view
category: Blocks
nav_order: 10
---

# Completion points view

Completion points view displays completion-point records supplied by the Course completion points local plugin. Learners can see their course links, points, notes, award dates, and running total from the beginning of the current calendar year.

## Key features

- Show the current user's completion points in a Moodle block on Dashboard or course pages.
- Present records in newest-first order with labelled table columns and a yearly total.
- Link each record to its course, with a fallback label when a course no longer exists.
- Allow specifically authorised staff to select another user's records.
- Show a clear empty state when no current-year records exist.
- Provide a static site-administration About page with installed release, compatibility, licence, maintainer, documentation, and support details.
- Work entirely within Moodle without external services, credentials, or build steps.

## Requirements

- Moodle 4.5 through Moodle 5.2 only.
- Course completion points (`local_completionpoints`) version `2026082400` or later, installed separately before this block.
- A database supported by the installed Moodle release. The block uses Moodle DML and no database-specific SQL.

The block displays existing records; it does not award points or manage course completion. Those functions belong to the required local plugin.

## Installation

Marketplace publication is pending. Obtain both plugin ZIPs from Pukunui for pre-release testing. Install Course completion points first, then upload the block ZIP through **Site administration > Plugins > Install plugins** and complete Moodle's validation and upgrade process. The block ZIP contains one `completionpoints_view` directory. No post-install command, Composer, or npm step is needed.

## Configuration and use

Turn editing on in Dashboard or a course page and add **Completion points view** to a block region. It reads the signed-in user's records from 1 January of the current year, using Moodle's user date/time handling. Narrow block drawers may require horizontal scrolling to read every table column.

An administrator or a user explicitly granted `block/completionpoints_view:viewotherusers` in the system context can add `userid=<Moodle user ID>` to the page URL to display another user's records. Unauthorised users cannot change the displayed user with this parameter. Invalid or deleted user IDs produce an invalid-user message. Legacy `id` links are retained where they do not conflict with the current course ID; new integrations should use `userid`.

Site administrators can open **Site administration > Plugins > Blocks > Completion points view > About**. The page derives release and supported versions from installed metadata. It contains no configuration form, tracking, or state-changing action.

## Privacy and permissions

The block reads user-linked point records for display but does not create, update, export, or delete the underlying data. It supplies a Privacy API null provider; Course completion points owns storage, metadata declarations, export, and deletion. No data is sent to an external service.

- `block/completionpoints_view:addinstance` controls adding the block to supported pages.
- `block/completionpoints_view:myaddinstance` controls adding it to Dashboard.
- `block/completionpoints_view:viewotherusers` protects cross-user access and has no default role assignment. Site administrators retain access.

Record notes and values are escaped for output, and queries use Moodle's parameterised DML API.

## Troubleshooting

- If no records appear, confirm that Course completion points is installed and has records for the displayed user dated in the current year.
- If a record was awarded near New Year, check the user's Moodle time zone and its creation date.
- If another user's records cannot be selected, check the system capability and use `userid`, not a course-page `id` parameter.
- If a course link is unavailable, confirm that the course still exists and the user has access to it.
- If the block is unavailable after installation, finish Moodle's upgrade and confirm that it is enabled in block management.
- Before upgrading beyond Moodle 5.2, obtain a release that explicitly supports the target version.

## Support and licence

- [Report a product bug](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=product-bug.yml)
- [Request a feature](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=feature.yml)
- [Report a documentation issue](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=documentation.yml)
- [Contact Pukunui Malaysia](mailto:hello.my@pukunui.com)

Completion points view is licensed under the GNU General Public License v3 or later. This documentation is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
