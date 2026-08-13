---
title: Skills card
parent: "Blocks"
nav_order: 40
permalink: /products/moodle-block_skillscard/
---

# Skills card

Skills card displays Moodle competency records as a compact block. It lists available competency short names and their scale rank or grade when scale data exists; users without records see **No competencies**.

## Requirements and installation

- Moodle 4.0 or later with competency data configured.
- Install at `blocks/skillscard`, complete the Moodle upgrade, and add **Skills card** to a supported block region.
- Multiple block instances are supported.

## Access and privacy

Users normally see their own data. Site administrators may inspect another user through Moodle's supported user-ID route; ordinary users cannot use that route to see another person's competency records.

The block reads Moodle competency data but does not create its own personal-data store. It declares Moodle's null privacy provider.

## Support

- [Report a bug or request a feature](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=product-bug.yml)
- [Pukunui Plugin Subscription Terms & Support Policy](https://pukunui.com/docs/policy-moodle-marketplace/)
- [Pukunui Malaysia](https://pukunui.com/home/location/malaysia/)

Original documentation copyright Pukunui Sdn Bhd and contributors, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---

Source: [moodle-block_skillscard at `991091dcda11`](https://github.com/PukunuiMalaysia/moodle-block_skillscard/commit/991091dcda114d77bf0e73aafbea1139c1857c57). [Report a documentation issue](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=documentation.yml).
