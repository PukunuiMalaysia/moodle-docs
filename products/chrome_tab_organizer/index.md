---
title: Chrome Tab Organizer & Productivity Tool
category: Related tools
parent: "Related tools"
nav_order: 20
permalink: /products/chrome_tab_organizer/
---

# Chrome Tab Organizer & Productivity Tool

Chrome Tab Organizer & Productivity Tool helps Chrome users organise large tab sessions, create reusable workspaces, group related tabs, and inspect open tabs in a vertical side panel. All organisation and workspace processing happens locally in the browser.

## Requirements and installation

- A current version of Google Chrome with Manifest V3, tab groups, and side-panel support.
- Install the extension from the official Chrome Web Store listing provided by Pukunui.
- Pin the extension to the Chrome toolbar if you want quick access to the popup.

After installation, open the extension popup to review the available actions or select **Open side panel** for a searchable vertical view of tabs across Chrome windows.

## Organise tabs

The popup provides actions for sorting tabs, moving matching sites into separate windows, grouping tabs by domain, creating local smart groups from tab titles or a prompt, tiling tabs, and closing duplicate URLs.

Actions show a preview of the affected tabs before running where practical. Pinned tabs and unsupported Chrome or extension pages are protected or skipped according to the extension settings. Review the preview before confirming any action that moves or closes tabs.

## Saved workspaces

Saved workspaces preserve restorable HTTP and HTTPS tabs, window groupings, active tabs, pinned state, and window geometry where Chrome makes that information available. Restoring a workspace creates new Chrome windows and does not replace the current session.

Workspace data is stored in `chrome.storage.local`. Unsupported pages are skipped and reported in the workspace status. Deleting a saved workspace removes that local snapshot.

## Side panel

The side panel presents tabs by window and domain, with search, collapsible groups, active-tab indication, and click-to-focus behaviour. Unsupported pages remain clearly identified instead of being treated as ordinary web tabs.

## Privacy and permissions

The extension processes open-tab titles and URLs locally so it can group, sort, search, and restore tabs. It does not send this information to Pukunui, analytics providers, advertising services, or an external AI service.

Settings and workspaces use Chrome local storage. Temporary undo layout data uses Chrome session storage and does not persist across browser restarts. The optional YouTube permission is used only when the user confirms tiling with the pause option enabled.

Chrome permissions support tab and window management, native tab groups, saved settings, display-aware tiling, the side panel, and the confirmed pause action. The extension does not inject advertising, rewrite links, or use affiliate tracking.

## Troubleshooting

- If an action reports skipped tabs, check for pinned tabs, Chrome internal pages, extension pages, or missing URLs.
- If the side panel is unavailable, update Chrome and confirm the extension is enabled.
- If a restored workspace contains fewer tabs than expected, review its skipped-tab count; unsupported pages are not saved.
- Closed duplicate tabs are not restored by the layout undo control.

## Support and licence

- [Pukunui Malaysia support](https://pukunui.com/home/location/malaysia/)
- [Report a documentation issue](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=documentation.yml)

The extension is licensed under the MIT License. Original documentation copyright Pukunui Sdn Bhd and contributors, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---

Source revision: `99e6cf2aa27e`. [Report a documentation issue](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=documentation.yml).
