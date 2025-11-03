# Using the Custom Extensions Config Parameter

## Overview

The BCTelemetry dashboard now uses a **parameter** for configuring which extensions to monitor. This makes it easy to use the same dashboard for multiple companies without editing queries.

---

## How to Change Configuration

### In Azure Data Explorer Dashboard

1. Open your dashboard in Azure Data Explorer
2. Look for the **"Custom Extensions Config"** parameter at the top of the page
3. Edit the text field with your configuration
4. Click **Apply** to update all queries

---

## Configuration Format

```
Publisher1:*,Publisher2:AppName,Publisher3:App1|App2
```

### Rules:
- **`,`** (comma) = Separates different publishers
- **`:`** (colon) = Separates publisher from app name(s)
- **`*`** (asterisk) = Include ALL extensions from this publisher
- **`|`** (pipe) = Separates multiple app names from same publisher

---

## Examples

### Current Configuration (Storkaup)
```
Storkaup:*,NVL:*,Stórkaup:*,Hagar:Liquor License,Wise:OrderProcess
```

**Meaning**:
- ✅ All extensions from **Storkaup**
- ✅ All extensions from **NVL**
- ✅ All extensions from **Stórkaup**
- ✅ Only **"Liquor License"** from **Hagar** (excludes Hagar Connect, Hagar Webshop)
- ✅ Only **"OrderProcess"** from **Wise** (excludes 5 other Wise extensions)

### Example for Another Company
```
CompanyA:*,CompanyB:*,Vendor1:CriticalApp,Vendor2:App1|App2|App3
```

**Meaning**:
- ✅ All extensions from **CompanyA**
- ✅ All extensions from **CompanyB**
- ✅ Only **"CriticalApp"** from **Vendor1**
- ✅ Three specific apps from **Vendor2**: "App1", "App2", "App3"

### Monitor Only Specific Extensions
```
Vendor1:App A,Vendor2:App B,Vendor3:App C
```

### Monitor All Custom Extensions
```
Publisher1:*,Publisher2:*,Publisher3:*
```

---

## How It Works Internally

The parameter is parsed in KQL like this:

```kql
let ConfigString = _CustomExtensionsConfig;
let CustomExtensionsToMonitor =
    ConfigString
    | extend Parts = split(ConfigString, ",")
    | mv-expand Part = Parts to typeof(string)
    | extend PublisherAndApps = split(Part, ":")
    | extend
        Publisher = tostring(PublisherAndApps[0]),
        Apps = tostring(PublisherAndApps[1])
    | extend AppList = split(Apps, "|")
    | mv-expand App = AppList to typeof(string)
    | project Publisher, App = tostring(App), IncludeAll = (App == "*")
    | distinct Publisher, App, IncludeAll;
```

Then queries join with this table to filter extensions.

---

## Finding Publisher Names

If you're unsure what publishers exist in your environment, run this query:

```kql
traces
| where timestamp > ago(30d)
| extend
    extensionPublisher = tostring(customDimensions.extensionPublisher),
    extensionName = tostring(customDimensions.extensionName)
| where isnotempty(extensionPublisher)
| where extensionPublisher != "Microsoft"
| summarize
    EventCount = count(),
    Extensions = make_set(extensionName)
    by extensionPublisher
| order by EventCount desc
```

---

## Which Queries Use This Parameter?

The parameter is used in these 3 queries on the **"Custom: Unused Objects"** page:

1. **Main View** - Shows all objects with usage statistics
2. **Critical Low Usage** - Highlights removal candidates
3. **Extension Summary** - Shows health per extension

---

## Benefits

✅ **One configuration for all queries** - Change once, applies everywhere
✅ **Easy to switch between companies** - Just change the parameter value
✅ **No query editing required** - All done through the UI
✅ **Supports complex scenarios** - Mix of "all" and "specific" extensions
✅ **Self-documenting** - Format is clear and visible in the parameter

---

## Troubleshooting

### Q: I changed the parameter but see no results

**A:** Check:
1. Publisher/extension names match exactly (case-sensitive)
2. Extensions have telemetry in the last 30 days
3. No typos in the configuration string
4. Clicked **Apply** after editing

### Q: How do I exclude all extensions from a publisher?

**A:** Simply don't include that publisher in the configuration string.

### Q: Can I monitor some extensions from a publisher but not others?

**A:** Yes! List them with `|` separator:
```
Publisher:App1|App2|App3
```

---

**Status**: ✅ Parameter-based configuration active
**Location**: Azure Data Explorer Dashboard → Custom: Unused Objects page
**Updated**: 2025-11-03
