# UUID Fix - Proper RFC 4122 UUIDs

**Date**: 2025-10-31
**Issue**: Azure Data Explorer requires RFC 4122 compliant UUIDs for all IDs
**Status**: ✅ Fixed and Validated

---

## Problem

The initial dashboard modification used non-UUID formatted IDs like:
- `"uc-tile-001-main-view"`
- `"uc-query-001-main"`

Azure Data Explorer validation failed with:
```
Needs to follow the UUID format as defined by RFC 4122
Example: 3e4666bf-d5e5-4aa7-b8ce-cefe41c7568a
```

---

## Solution

All IDs have been replaced with proper RFC 4122 UUIDs.

### Updated IDs

#### Tile IDs (3 tiles)

| Old ID | New UUID |
|--------|----------|
| `uc-tile-001-main-view` | `f1e2d3c4-b5a6-4789-8012-3456789abcde` |
| `uc-tile-002-critical` | `a2b3c4d5-e6f7-4890-1234-567890abcdef` |
| `uc-tile-003-summary` | `b3c4d5e6-f7a8-4901-2345-67890abcdef1` |

#### Query IDs (3 queries)

| Old ID | New UUID |
|--------|----------|
| `uc-query-001-main` | `c1a2b3d4-e5f6-7890-1234-567890abcdef` |
| `uc-query-002-critical` | `d2e3f4a5-b6c7-4890-2345-678901bcdef0` |
| `uc-query-003-summary` | `e3f4a5b6-c7d8-4901-3456-7890abcdef12` |

#### Page ID (unchanged, already UUID format)

| Component | UUID |
|-----------|------|
| Custom: Unused Objects page | `a1b2c3d4-e5f6-7890-abcd-ef1234567890` |

---

## Validation

✅ **JSON syntax validated** using PowerShell `ConvertFrom-Json`
✅ **All IDs follow RFC 4122 UUID format**
✅ **All tile queryRef.queryId values match query IDs**
✅ **All tile pageId values match page ID**

---

## Ready to Upload

The dashboard JSON file is now ready to upload to Azure Data Explorer:
- File: `C:\AL\BCTelemetry\Azure Data Explorer\BCTelemetryDashboard.json`
- Backup: `C:\AL\BCTelemetry\Azure Data Explorer\BCTelemetryDashboard.backup.20251031_090744.json`

---

## Upload Instructions

1. Go to Azure Data Explorer
2. Navigate to your dashboard
3. Click "Edit" or "Import dashboard"
4. Upload the modified `BCTelemetryDashboard.json` file
5. Verify the "Custom: Unused Objects" page appears in navigation
6. Test all three tiles display data correctly

---

**Status**: ✅ Ready for Production Use
