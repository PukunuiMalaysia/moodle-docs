---
title: QuickNav LMS by Pukunui
category: Related tools
parent: "Related tools"
nav_order: 30
permalink: /products/quicknav-lms/
---

# QuickNav LMS by Pukunui

QuickNav LMS by Pukunui is a Chrome side-panel extension that provides role-based shortcuts and context-aware links for LMS sites, including sites running Moodle™ software. It helps students, teachers, administrators, and support teams reach common LMS pages without changing the LMS itself.

## Requirements and installation

- A current version of Google Chrome with Manifest V3 and side-panel support.
- Access to an HTTP or HTTPS LMS site.
- Install the extension from the official Chrome Web Store listing provided by Pukunui.

After installation, open an LMS page, select the QuickNav extension action, and open the side panel. QuickNav detects the current site and enables shortcuts whose required URL context is available.

## Choose shortcuts

QuickNav organises shortcuts into Student, Teacher, Admin, and Support views. Search covers shortcut labels, descriptions, keywords, groups, and paths. Favourites are stored for each LMS base URL and role, and users can add their own shortcuts for a site.

Course, activity, user, or category shortcuts are enabled only when the corresponding identifier is available in the active page URL. The LMS continues to enforce its normal permissions; QuickNav does not bypass authentication, roles, or capabilities.

## Site and version detection

QuickNav supports root and subdirectory LMS installations. It derives context from the active tab URL and safe page markers. For Moodle sites, it may request known static, same-origin release or readme files to estimate the Moodle release or branch.

If automatic base-URL detection is unsuitable for a customised site, save a manual LMS base URL override for that site origin. Version, theme, plugin, routing, and permission differences can still cause an LMS page to redirect or deny access.

## Privacy and local data

QuickNav stores the selected role, favourites, custom shortcuts, LMS base-URL overrides, and interface preferences locally using `chrome.storage.local`.

It does not collect or transmit LMS content, grades, student records, messages, names, passwords, browsing history, analytics, or advertising data. It does not inject advertisements, modify LMS links, add tracking parameters, or send settings to an external service. Pukunui support and resource links open only when the user selects them.

## Permissions

The extension uses:

- `sidePanel` for its primary interface;
- `activeTab` and `tabs` to identify the current tab and URL;
- `storage` for local settings, favourites, and shortcuts; and
- `scripting` for a limited active-tab Moodle marker probe when Chrome permits it.

QuickNav does not request broad host permissions or `<all_urls>` access.

## Troubleshooting

- If course shortcuts are disabled, open a course page whose URL contains a course ID.
- If a shortcut opens the wrong site path, set a manual base URL for that LMS origin.
- If an administration shortcut is denied, confirm the signed-in LMS account has the required permission.
- Some routes differ between LMS versions, themes, and installed plugins; report reproducible route problems with the LMS version and starting URL, without including personal or confidential LMS data.

## Support, licence, and trademark

- [Pukunui Malaysia support](https://pukunui.com/home/location/malaysia/)
- [Report a documentation issue](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=documentation.yml)

QuickNav LMS by Pukunui is licensed under the MIT License. Original documentation copyright Pukunui Sdn Bhd and contributors, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

Moodle™ is a trademark of Moodle Pty Ltd. QuickNav LMS by Pukunui is not affiliated with, endorsed by, or sponsored by Moodle Pty Ltd.

---

Source revision: `7c94408d25dd`. [Report a documentation issue](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=documentation.yml).
