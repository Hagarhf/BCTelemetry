# Generic Extension Filter Configuration Guide

## Overview

The dashboard queries are now **generic** and use a configurable **datatable** to specify which extensions to monitor. This makes it easy to use the same dashboard for multiple companies.

---

## How It Works

Each query starts with a `CustomExtensionsToMonitor` datatable:

```kql
let CustomExtensionsToMonitor = datatable(extensionPublisher: string, extensionName: string, IncludeAll: bool)
[
    "Storkaup", "", true,              // All extensions from Storkaup
    "NVL", "", true,                   // All extensions from NVL
    "Hagar", "Liquor License", false   // Only "Liquor License" from Hagar
];
```

### Columns:
- **extensionPublisher**: Publisher name (e.g., "Storkaup", "Hagar", "Wise")
- **extensionName**: Specific extension name (empty string "" means all)
- **IncludeAll**:
  - `true` = Include all extensions from this publisher
  - `false` = Only include the specific extension named in extensionName

---

## Current Configuration (Storkaup Company)

```kql
let CustomExtensionsToMonitor = datatable(extensionPublisher: string, extensionName: string, IncludeAll: bool)
[
    "Storkaup", "", true,                 // ✅ All Storkaup extensions
    "NVL", "", true,                      // ✅ All NVL extensions
    "Stórkaup", "", true,                 // ✅ All Stórkaup extensions
    "Hagar", "Liquor License", false,     // ✅ Only "Liquor License"
    "Wise", "OrderProcess", false         // ✅ Only "OrderProcess"
];
```

**Result**: Monitors 5 extensions:
1. Storkaup (from Storkaup)
2. WebStore (from NVL)
3. Storkaup Addons (from Stórkaup)
4. Liquor License (from Hagar) - excludes Hagar Connect & Hagar Webshop
5. OrderProcess (from Wise) - excludes other 5 Wise extensions

---

## How to Configure for Another Company

### Step 1: Get Publisher Information

Run this query to see what extensions exist:

```kql
traces
| where timestamp > ago(30d)
| extend
    extensionPublisher = tostring(customDimensions.extensionPublisher),
    extensionName = tostring(customDimensions.extensionName)
| where isnotempty(extensionPublisher)
| where extensionPublisher != "Microsoft"  // Exclude Microsoft
| summarize
    EventCount = count(),
    Extensions = make_set(extensionName)
    by extensionPublisher
| order by EventCount desc;
```

### Step 2: Update the Datatable

Edit the datatable at the top of each query in Azure Data Explorer:

**Example for Company B:**

```kql
let CustomExtensionsToMonitor = datatable(extensionPublisher: string, extensionName: string, IncludeAll: bool)
[
    // Monitor all extensions from these publishers
    "CompanyB", "", true,
    "CustomVendor", "", true,

    // Monitor only specific extensions from these publishers
    "Navax", "Advanced Intercompany", false,
    "Navax", "Easy Fixed Assets", false,
    "Vinna", "Vinna Logistics", false
];
```

### Step 3: Which Queries to Update

Update the datatable in these 3 queries:
1. **Main View** (Query ID: `c1a2b3d4-e5f6-7890-1234-567890abcdef`)
2. **Critical Low Usage** (Query ID: `d2e3f4a5-b6c7-4890-2345-678901bcdef0`)
3. **Extension Summary** (Query ID: `e3f4a5b6-c7d8-4901-3456-7890abcdef12`)

---

## Configuration Examples

### Example 1: Monitor All Custom Extensions

```kql
let CustomExtensionsToMonitor = datatable(extensionPublisher: string, extensionName: string, IncludeAll: bool)
[
    "Publisher1", "", true,
    "Publisher2", "", true,
    "Publisher3", "", true
];
```

### Example 2: Mix of All and Specific

```kql
let CustomExtensionsToMonitor = datatable(extensionPublisher: string, extensionName: string, IncludeAll: bool)
[
    // All from these
    "InHouseTeam", "", true,
    "TrustedVendor", "", true,

    // Only specific ones from these
    "LargeVendor", "CriticalApp1", false,
    "LargeVendor", "CriticalApp2", false,
    "LargeVendor", "CriticalApp3", false
];
```

### Example 3: Only Specific Extensions

```kql
let CustomExtensionsToMonitor = datatable(extensionPublisher: string, extensionName: string, IncludeAll: bool)
[
    "Vendor1", "App A", false,
    "Vendor1", "App B", false,
    "Vendor2", "App C", false,
    "Vendor3", "App D", false
];
```

---

## Quick Reference: Include Logic

| IncludeAll | extensionName | Result |
|------------|---------------|--------|
| `true` | `""` (empty) | ✅ Include ALL extensions from this publisher |
| `false` | `"SpecificApp"` | ✅ Include ONLY "SpecificApp" from this publisher |
| `false` | `""` (empty) | ❌ Won't match anything (invalid configuration) |

---

## How to Update Dashboard for Another Company

### Option A: Edit in Azure Data Explorer UI (Recommended)

1. Open your dashboard in Azure Data Explorer
2. Click **Edit** on the "Custom: Unused Objects" page
3. Click on each tile to edit its query
4. Find the `CustomExtensionsToMonitor` datatable at the top
5. Update the datatable with your company's configuration
6. Click **Apply** and **Save**

### Option B: Edit the JSON File

1. Open `BCTelemetryDashboard.json`
2. Search for `CustomExtensionsToMonitor`
3. You'll find it in 3 places (the 3 queries)
4. Update all 3 occurrences with your configuration
5. Save and upload to Azure Data Explorer

---

## Configuration Template

Use this template to configure for a new company:

```kql
let CustomExtensionsToMonitor = datatable(extensionPublisher: string, extensionName: string, IncludeAll: bool)
[
    // === STEP 1: Add publishers to include ALL their extensions ===
    "PublisherName1", "", true,
    "PublisherName2", "", true,

    // === STEP 2: Add specific extensions from publishers with many extensions ===
    "PublisherWithManyApps", "ImportantApp1", false,
    "PublisherWithManyApps", "ImportantApp2", false,

    // === STEP 3: Continue for all custom extensions to monitor ===
    // Add more rows as needed...
];
```

---

## Benefits of This Approach

✅ **No hardcoded values** - Easy to change per company
✅ **Self-documenting** - Configuration is at the top of each query
✅ **Flexible** - Mix "all from publisher" and "specific extensions"
✅ **Maintainable** - Only update the datatable, query logic stays the same
✅ **Scalable** - Works for any number of extensions

---

## Troubleshooting

### Q: I updated the datatable but see no results

**A:** Check:
1. Publisher name spelling matches exactly (case-sensitive)
2. Extension name spelling matches exactly (if IncludeAll = false)
3. Extensions have telemetry in the time range (run the discovery query)

### Q: How do I find the exact publisher and extension names?

**A:** Run the discovery query from Step 1 above, or use:
```kql
traces
| where timestamp > ago(7d)
| extend
    extensionPublisher = tostring(customDimensions.extensionPublisher),
    extensionName = tostring(customDimensions.extensionName)
| where extensionPublisher == "YourPublisher"  // Replace with your publisher
| summarize by extensionName
| order by extensionName asc;
```

### Q: Can I exclude Microsoft extensions?

**A:** Yes! Just don't add Microsoft to the datatable. Only extensions in the datatable are included.

---

## Files Reference

| File | Purpose |
|------|---------|
| `BCTelemetryDashboard.json` | Dashboard with generic queries |
| `EXTENSION-FILTER-CONFIGURATION.md` | This guide |
| `CHECK-ALL-PUBLISHERS.kql` | Discovery query to find publishers |
| `Storkaup_ExtensionPublishers.csv` | Example output from Storkaup company |

---

**Status**: ✅ Queries are now generic and configurable
**Location**: `C:\AL\BCTelemetry\Azure Data Explorer\`
