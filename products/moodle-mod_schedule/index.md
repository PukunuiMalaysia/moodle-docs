---
title: Schedule
parent: "Activities"
nav_order: 10
permalink: /products/moodle-mod_schedule/
---

# Schedule

Schedule is a Moodle activity for events with a booking period and a defined number of seats. It can be used for laboratory sessions, examinations, appointments, or other reservable course events.

## Requirements and installation

- Moodle 4.0 or later as declared by the current package.
- Install at `mod/schedule`, complete the Moodle upgrade, and add a **Schedule** activity to a course.
- The package includes database schema, scheduled tasks, privacy support, and import and export utilities. Validate backup and restore behaviour for your deployed release before production use.

## Teacher workflow

Teachers define the event time, booking opening and closing dates, capacity, optional profile-field sublimits, overbooking policy, notes, grade or scale, and what reservation details students may see. Teachers can reserve seats for users, message participants, grade after the event, and download reservation lists.

Administrators can configure displayed profile fields and import reservations from CSV. Test imports with non-production data first.

## Privacy

The activity stores reservation user IDs, timestamps, cancellation state, grades, grader IDs, notification state, and optional user notes. Moodle's Privacy API supports metadata, export, and deletion. Limit activity and report capabilities to appropriate staff and avoid exporting more profile information than required.

## Support

- [Report a bug or request a feature](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=product-bug.yml)
- [Pukunui Plugin Subscription Terms & Support Policy](https://pukunui.com/docs/policy-moodle-marketplace/)
- [Pukunui Malaysia](https://pukunui.com/home/location/malaysia/)

Original documentation copyright Roberto Pinna, Pukunui Sdn Bhd, and contributors. New material is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); existing notices remain applicable.

---

Source: [moodle-mod_schedule at `c922ed6b64f6`](https://github.com/PukunuiMalaysia/moodle-mod_schedule/commit/c922ed6b64f679ee093045a0f0fe8c9b1fc299ab). [Report a documentation issue](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=documentation.yml).
