---
title: SocialLink
parent: "Blocks"
nav_order: 50
permalink: /products/moodle-block_sociallink/
---

# SocialLink

SocialLink adds configurable sharing links to Moodle pages, courses, activities, and the site front page. Available destinations include Facebook, X, LinkedIn, WhatsApp, Telegram, email, Microsoft Teams, Reddit, Bluesky, and the browser clipboard.

## Requirements and installation

- Moodle 4.5 through 5.2.
- Install at `blocks/sociallink`, complete the Moodle upgrade, and configure default providers under **Site administration > Plugins > Blocks > SocialLink**.
- Add the block where sharing links should appear, then choose page scope, layout, providers, optional title, and introductory text.

No provider API credential or third-party JavaScript widget is required.

## Privacy and external services

The block stores only site and block-instance configuration. It does not store personal data and does not contact social networks on page load. When a user follows a share link, they leave Moodle and the selected service may process the shared URL and browser or signed-in account information under that service's terms.

## Support

- [Report a bug or request a feature](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=product-bug.yml)
- [Pukunui Plugin Subscription Terms & Support Policy](https://pukunui.com/docs/policy-moodle-marketplace/)
- [Pukunui Malaysia](https://pukunui.com/home/location/malaysia/)

Original documentation copyright Pukunui Sdn Bhd and contributors, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---

Source: [moodle-block_sociallink at `a4cd437bf4bf`](https://github.com/PukunuiMalaysia/moodle-block_sociallink/commit/a4cd437bf4bfac88e994a428ad815cf2ec93e10e). [Report a documentation issue](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=documentation.yml).
