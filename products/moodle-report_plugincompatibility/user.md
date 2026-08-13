---
title: Administrator guide
parent: "Third-party plugin compatibility"
grand_parent: "Reports"
---

# Third-party Plugin Compatibility Report - User Documentation

## Overview

The Third-party Plugin Compatibility Report is a Moodle admin tool that helps site administrators and IT teams plan Moodle upgrades by analysing the compatibility of installed third-party plugins with different Moodle versions.

This report provides critical information about whether your current plugins will work with a target Moodle version, helping you make informed decisions about upgrades and identify potential compatibility issues before they occur.

## Features

- **Third-party Plugin Analysis**: Displays only contributed (non-core) plugins installed on your site
- **Version Compatibility Checking**: Verifies if your installed plugin versions are compatible with a selected Moodle version
- **Plugin Availability Status**: Shows whether plugins have compatible releases available on moodle.org
- **Dynamic Version Selection**: Easy dropdown to select any target Moodle version for analysis
- **Visual Status Indicators**: Colour-coded status indicators for quick identification of compatibility issues
- **Source URL Links**: Direct links to plugin pages on moodle.org when available
- **Performance Optimisation**: Built-in caching to improve loading times

## System Requirements

- Moodle 4.1 or higher
- PHP 7.4 or higher
- cURL extension enabled
- Internet connectivity to access moodle.org

## Installation

### Step 1: Download and Install

1. Download the plugin files from your source
2. Log in as a site administrator
3. Navigate to **Site Administration → Plugins**
4. Click **Install plugins**
5. Follow the installation prompts to complete the setup

![installation_1](https://github.com/user-attachments/assets/a9733fc6-7559-4dbd-8b3e-af9cf60fc666)
![installation_2](https://github.com/user-attachments/assets/f6923958-0683-40c7-981c-a70f9adfabaf)
![installation_3](https://github.com/user-attachments/assets/cd2fd94f-2b66-45e8-b91a-11a9bd841f64)

### Step 2: Verify Installation

After installation, verify that the plugin appears in your reports:

1. Go to **Site Administration → Reports**
2. Look for "Third-party Plugin Compatibility" in the list

![reports_menu](https://github.com/user-attachments/assets/1f41eaa7-4578-478c-9db4-92a5028b07d4)

## Accessing the Report

### Required Permissions

To access the report, you need the `report/plugincompat:view` capability. This is automatically granted to:
- Site administrators
- Managers (by default)

### Navigation

1. Log in as a site administrator
2. Navigate to **Site Administration → Reports → Third-party Plugin Compatibility**

## Using the Report

### Initial Setup

When you first access the report, you'll see:

1. **Version Selector**: A dropdown menu to select your target Moodle version
2. **Plugin Table**: Status columns initialised to "-" until you select a version

![initial_report_interface](https://github.com/user-attachments/assets/563e6b60-8841-4327-ad08-53df2a7d8ba3)

### Selecting a Target Version

1. Click on the **"Select Moodle version"** dropdown
2. Choose the Moodle version you want to check compatibility for
3. The report will automatically update to show compatibility information

![version_dropdown](https://github.com/user-attachments/assets/494a6045-bcd7-4bd8-86ff-7d66acc05d10)

### Understanding the Report Table

The report displays a table with the following columns:

#### Plugin Name
- Shows the full name of each installed third-party plugin
- Excludes core Moodle plugins to focus on contributed plugins only

#### Installed Version
- Displays the version number of the plugin currently installed on your site
- Shows the release date code (YYYYMMDDXX format) when available

#### Source URL
- Provides a direct link to the plugin's page on moodle.org
- Shows "no plugin page" for plugins not available in the official directory

#### Installed Version Compatibility
This column indicates whether your currently installed plugin version is compatible with the selected Moodle version:

- **COMPATIBLE** (Green): The installed version supports the target Moodle version
- **NOT COMPATIBLE** (Red): The installed version does not support the target Moodle version
- **NO PLUGIN PAGE**: No data as plugin cannot be found on moodle.org
- **-** (Gray): No version selected

#### Other Compatible Versions
This column shows whether the plugin has any releases available that supports the target Moodle version:

- **AVAILABLE** (Green): The plugin has releases that support the target Moodle version
- **NOT AVAILABLE** (Red): The plugin has no releases that support the target Moodle version
- **NO PLUGIN PAGE**: No data as plugin cannot be found on moodle.org
- **-** (Gray): No version selected

![complete_report_table](https://github.com/user-attachments/assets/b34d52b7-4c8d-4bca-bcbc-a7e67681db1d)

## Interpreting Results

### Scenario 1: Compatible Plugin
- **Installed Version Compatibility**: COMPATIBLE
- **Other Compatible Versions**: AVAILABLE

![status_scenario_1](https://github.com/user-attachments/assets/88abeaee-31c5-40d8-abe0-72d8be47da36)

### Scenario 2: Plugin Needs Update
- **Installed Version Compatibility**: NOT COMPATIBLE
- **Other Compatible Versions**: AVAILABLE

![status_scenario_2](https://github.com/user-attachments/assets/351ff848-11ef-4674-b45a-5ca4ce5b4ab9)

### Scenario 3: Plugin Not Available
- **Installed Version Compatibility**: NOT COMPATIBLE
- **Other Compatible Versions**: NOT AVAILABLE

![status_scenario_3](https://github.com/user-attachments/assets/65827705-f2e1-42dd-b7ca-548405ed2c9d)

### Scenario 4: Plugin Not on Moodle.org
- **Source URL**: Shows "no plugin page"

![status_scenario_4](https://github.com/user-attachments/assets/8021ee77-c74d-416f-ad04-98f2bcd94f2d)

## Performance Considerations

1. **First Load**: The initial report generation may take some time as it fetches data from moodle.org
2. **Caching**: Subsequent loads will be faster due to built-in caching
3. **Off-Peak Usage**: Consider running the report during off-peak hours for better performance

## Troubleshooting

### Common Issues

#### Slow Loading Times
**Problem**: The report takes a long time to load
**Solution**:
- Wait for the initial load to complete - subsequent loads will be faster
- Check your internet connection
- Try accessing the report during off-peak hours

#### Error Message
**Problem**: Error messages appear instead of compatibility information
**Solution**:
- Verify internet connectivity
- Check that your server can access moodle.org
- Try again later if moodle.org is limiting your requests

#### Missing Plugin Information
**Problem**: Some plugins show "No plugin page" or limited information
**Solution**:
- The plugin may not be listed on moodle.org
- Contact the plugin developer directly for compatibility information
- Check if the plugin has been renamed or relocated

#### Outdated Information
**Problem**: The compatibility information seems outdated
**Solution**:
- Plugin data is cached for performance - wait for cache expiration (1-24 hours)
- Check the plugin's moodle.org page directly for the most current information

### Getting Help

If you encounter issues not covered in this documentation:

1. **Check Moodle Logs**: Look for error messages in Site Administration → Reports → Logs
2. **Enable Debugging**: Temporarily enable developer-level debugging to see detailed error messages
3. **Contact Support**: Reach out to your Moodle administrator or the plugin developer

## Frequently Asked Questions

### Q: Why don't I see core Moodle plugins in the report?
**A**: The report focuses on third-party plugins only, as core plugins are automatically updated with Moodle itself.

### Q: How often is the compatibility data updated?
**A**: The plugin fetches data from moodle.org in real-time, but caches results for 1-24 hours for performance.

### Q: Can I check compatibility for custom plugins?
**A**: Yes, but only if they're listed on moodle.org. Custom plugins not in the directory will show limited information.

### Q: What if a plugin shows as "Not Compatible" but I know it works?
**A**: Plugin developers may not have updated their compatibility information. Check the plugin's documentation or contact the developer.

### Q: How accurate is the compatibility information?
**A**: The information is based on data provided by plugin developers on moodle.org. It's always accurate but should be verified again after purging the cache.

## Security and Privacy

The Third-party Plugin Compatibility Report:
- Does not store any personal data
- Only accesses publicly available information from moodle.org
- Does not transmit sensitive information about your site
- Complies with Moodle's privacy standards

## Additional Resources

- [Moodle Plugin Directory](https://moodle.org/plugins/)
- [Moodle Upgrade Documentation](https://docs.moodle.org/en/Upgrading)
- [Plugin Installation Guide](https://docs.moodle.org/en/Installing_plugins)
- [Moodle Version Support](https://docs.moodle.org/dev/Releases)

---

*Last updated: July 2025*
*Plugin version: 1.0.0*
