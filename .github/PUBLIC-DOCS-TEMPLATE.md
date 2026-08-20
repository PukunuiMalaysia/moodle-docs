# Public product index template

Use this exact H2 structure for every product-facing `docs/public/index.md`. Replace bracketed instructions with source-faithful product information and remove the brackets before review.

```markdown
---
title: Product name
category: Product category
nav_order: 10
---

# Product name

[Identify the intended user, the problem the product solves, and its principal benefit in one or two concise paragraphs.]

## Key features

- [Describe a product-owned capability as a user benefit.]

## Screenshots

### [Workflow name]

![Meaningful description of the current product interface](images/descriptive-kebab-case.png)
*[Explain what the screenshot demonstrates.]*

All people and content shown are fictional demonstration data.

## Requirements

- [State supported Moodle or Chrome versions and required dependencies.]

## Installation

[For a pre-release Moodle plugin: state that Marketplace publication is pending and explain that a provided pre-release ZIP can be installed through **Site administration > Plugins > Install plugins**. For another published Moodle plugin: link to its verified Moodle Marketplace page, download the ZIP, and install it through **Site administration > Plugins > Install plugins**. For a browser extension: link to its official Chrome Web Store page.]

## Configuration and use

### [Administrator workflow]

[Describe configuration and normal operation using visible interface labels.]

## Privacy and permissions

[Explain stored or processed data, external services, Moodle capabilities or Chrome permissions, and relevant boundaries.]

## Troubleshooting

- [Describe a likely symptom and the administrator action that resolves or diagnoses it.]

## Support and licence

- [Report a product problem](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=product-bug.yml)
- [Report a documentation problem](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=documentation.yml)
- [Pukunui Malaysia support](https://pukunui.com/location/malaysia/)

[State the software licence and the CC BY 4.0 documentation licence.]
```
