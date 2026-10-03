---
title: Image optimizer
category: Local plugins
nav_order: 50
---

# Image optimizer

Image optimizer helps site administrators reduce the size of eligible existing JPEG and PNG images in Moodle's File API. The Settings, Report and About tabs provide a collect, preview and approve workflow. Inventory collection and previews leave original images unchanged; replacement requires explicit approval of a completed preview within seven days.

## Key features

- Collect a paginated inventory of recorded images, including protected and unsupported files, and filter or sort the report before previewing eligible matches across all filtered pages.
- Optimize only reviewed teaching-content areas: course summary and overview images, Page content, Text and media areas, and Book chapters.
- Protect submissions, feedback, private files, other unreviewed file areas, repository aliases and images referenced by aliases.
- Review estimated reductions before approving replacements. Completed logical file-size reductions are reported separately and do not measure immediate physical disk reclamation.
- Preserve file IDs, filenames, Moodle URLs, ownership, source information and supported embedded metadata when replacing images.
- Run bounded, resumable background jobs through Moodle cron, continuing after the browser closes. A shared lock prevents overlapping image operations.
- Optionally schedule inventory refreshes and preview preparation. Scheduled work never approves replacements, and new installations leave recurring work disabled.
- Use PHP GD for image processing, with configurable JPEG quality, minimum image size and optional resizing. No external image-processing service is used.

## Screenshots

### Settings

![Image optimizer settings](images/image-optimizer-settings.png)

*New installations leave scheduled inventory refreshes and previews disabled. Settings control processing quality, batch limits and optional resizing. All site names and content shown are fictional demonstration data.*

### Report

![Image optimizer Report tab showing an inventory and completed preview awaiting approval](images/image-optimization-report.png)

*The report provides collection, filtering, preview and approval controls. Previewed images remain unchanged until an administrator approves replacement. All files and course names shown are fictional demonstration data.*

### About

![Image optimizer About page showing release, compatibility and support links](images/image-optimizer-about.png)

*The About tab derives its release and compatibility details from installed plugin metadata and provides documentation, support and licence links.*

## Requirements

- Moodle 4.5 through Moodle 5.2.
- PHP GD for image processing and zlib for PNG recompression.
- PHP EXIF support to read JPEG EXIF orientation; affected images are skipped if that support is unavailable.
- Working Moodle cron for background jobs, including operations started from the Report tab.
- No additional Moodle plugin or external service is required.

## Installation

Marketplace publication is pending. If Pukunui has provided the pre-release Image optimizer plugin ZIP, open **Site administration > Plugins > Install plugins**, upload the ZIP, complete validation, and follow the displayed upgrade steps. No manual dependency installation is required.

## Configuration and use

### Configure processing

Open **Site administration > Plugins > Local plugins > Image optimizer**. Use **Settings** to configure JPEG quality, the minimum image size, images per processing batch and the maximum processing time per batch. Optionally enable resizing and set maximum width and height. Lower JPEG quality and resizing can reduce visual detail. PNG compression without resizing is lossless.

Keep a current database and file-storage backup before approving replacements: there is no built-in undo. Supported embedded metadata and orientation are retained automatically; this is not an optional EXIF-preservation setting. Unknown metadata, animation, unsupported colour encodings and unsafe inputs are skipped. Images exceeding the byte, pixel, dimension or estimated memory safeguards remain visible in the inventory but are not processed.

### Collect and preview

1. Open **Report**, choose **Collect/refresh inventory**, and confirm collection. Collection reads recorded file metadata without replacing images.
2. Wait for background collection to finish. Filter and sort the report to identify the images to review; protected and unsupported images remain identifiable.
3. Choose **Preview filtered images** and confirm. The preview includes eligible matches across every filtered page and does not replace original files.
4. Review the completed preview, estimated reductions and per-file results.

### Approve reviewed images

Choose **Optimize reviewed images** within seven days of preview completion. Confirm that you have reviewed the preview and have a current database and file-storage backup, then approve replacement. The job processes the frozen preview membership in background batches.

A preview cannot be reused after optimization has been requested. Expired previews or changed processing settings require a fresh preview. Files changed since collection or preview are skipped, and replacements must match the reviewed output. Only smaller outputs are installed. The completed report distinguishes actual replacements from estimates, skipped images and failures.

### Optional recurring preparation

Enable **Enable scheduled inventory refresh and previews** only if recurring preparation is wanted. Keep Moodle cron running and review the scheduled-task status shown in Settings. Recurring work collects inventory and prepares previews; an administrator must still approve replacements from Report. Batch controls limit each processing slice, not the total number of filtered images in a job.

## Privacy and permissions

Only users with Moodle's site-configuration capability can access the administration workflow. Images and personal data are not sent to an external service.

The plugin stores four groups of related data: optimization statistics, image inventory, per-file preview and replacement results, and background operation requests. These can include file owners and contexts, filenames and logical file paths, course and activity names, content fingerprints, requesting users, frozen settings and filters, progress and timestamps. Moodle's Privacy API describes the retained fields and supports discovery, export and deletion, including retained ownership metadata after an original file is deleted.

Privacy deletion removes plugin records, not the original files managed by their owning Moodle components. Operation history is retained for 30 days; inventories needed by retained jobs remain until those jobs expire.

## Troubleshooting

- If a queued job does not progress, check Moodle cron and scheduled/ad hoc task failures. Closing the browser does not stop a job.
- If an image cannot be previewed, check its eligibility reason, minimum size, supported format and safety limits, and confirm PHP GD and zlib are available.
- If a JPEG with orientation metadata is skipped, check PHP EXIF availability.
- If approval is unavailable, complete a fresh preview using the current processing settings and approve within seven days.
- A result indicating that the image cannot be compressed means processing did not produce a smaller acceptable output. An invalid-image result indicates that the source could not be safely processed.
- If another operation is active, allow it to finish or use **Stop operation** in Report. Incomplete collection does not replace the previous complete inventory.
- If updated interface text is not visible after upgrading, purge Moodle caches and reload the page.

## Support and licence

- [Report an Image optimizer product issue](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=product-bug.yml)
- [Request an Image optimizer feature](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=feature.yml)
- [Report a documentation issue](https://github.com/PukunuiMalaysia/moodle-docs/issues/new?template=documentation.yml)
- [Pukunui Plugin Subscription Terms & Support Policy](https://pukunui.com/docs/policy-moodle-marketplace/)
- [Pukunui Malaysia support](https://pukunui.com/location/malaysia/)

Image optimizer is licensed under the GNU General Public License v3 or later. This documentation is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
