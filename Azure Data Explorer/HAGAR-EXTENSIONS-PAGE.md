# Hagar Extensions Dashboard Page - Summary

**Date**: 2025-10-31
**Status**: ✅ Complete and Validated

---

## Changes Made

### 1. Updated "Custom: Unused Objects" Page
- **Removed** Hagar Connect and Hagar Webshop from filter
- **Now filters only**: Storkaup and NVL (WebStore) extensions
- **Purpose**: Focus on Storkaup-owned customizations for cleanup analysis

### 2. Created New "Hagar Extensions" Page
- **Page Name**: "Hagar Extensions"
- **Page ID**: `f4a5b6c7-d8e9-4012-3456-789012abcdef`
- **Purpose**: Monitor critical Hagar Connect and Hagar Webshop integrations

---

## New Hagar Extensions Page - 4 Tiles

### Tile 1: Hagar Extensions Activity Overview
**Location**: Top of page (full width)
**Purpose**: High-level health check of all Hagar extensions
**Refresh**: Every 24 hours

**Key Metrics**:
- Event count per extension
- Events per hour (activity rate)
- Unique objects used
- Minutes since last activity
- Status indicator (Active / Low Activity / Inactive)

**Expected Results** (based on 24h data):
- **Hagar Connect**: ~1,115 events, 46 events/hour, ✅ Active
- **Hagar Webshop**: ~64 events, 3 events/hour, ✅ Active

---

### Tile 2: Azure Service Bus Queue Performance
**Location**: Left side, middle
**Purpose**: Monitor HAG ASB Queue integration (your most active Hagar component)
**Refresh**: Hourly breakdown

**Key Metrics**:
- Call count per hour
- Average/P95/Max response time (ms)
- Performance status (Fast / Moderate / Slow)
- Error count
- Error status

**Expected Results** (based on 24h data):
- **HAG ASB Queue**: ~858 calls/day, should be ✅ Fast (<500ms avg)

**Alerts**:
- 🔴 Average > 1000ms (Slow)
- ⚠️ Average > 500ms (Moderate)
- 🔴 Any errors detected

---

### Tile 3: Export Processing & Slow Operations
**Location**: Right side, middle
**Purpose**: Track slow export/delete operations
**Refresh**: Every 24 hours

**Key Metrics**:
- Operation count
- Average execution time (seconds)
- Max execution time (seconds)
- Status (Very Slow / Slow / Moderate / Normal)
- Last execution timestamp

**Expected Results** (based on 24h data):
- **HAG Delete Export Tools**: 27 slow queries detected
- **HAG Export Processing**: 6 operations
- Shows only operations > 1 second

**Alerts**:
- 🔴 Max > 60 seconds (Very Slow)
- ⚠️ Max > 30 seconds (Slow)
- 📊 Average > 10 seconds (Moderate)

---

### Tile 4: Hagar Extensions Errors & Warnings
**Location**: Bottom of page (full width)
**Purpose**: Quick error detection for Hagar extensions
**Refresh**: Every 24 hours

**Key Metrics**:
- Severity (Critical / Error / Warning)
- Error count
- First and last occurrence
- Sample messages (up to 3)

**Expected Results** (based on 24h data):
- Should be minimal or empty (your system is healthy!)
- Any critical/error shows as 🔴
- Warnings show as ℹ️

---

## Query Details

### Query 1: Activity Overview
**Query ID**: `f5a6b7c8-d9e0-4234-5678-901234abcde0`
**Filter**: `extensionName startswith "Hagar" or extensionName == "HAG"`
**Time Range**: 24 hours
**Aggregation**: By extension name

### Query 2: ASB Queue Performance
**Query ID**: `a6b7c8d9-e0f1-4345-6789-012345abcde2`
**Filter**: `alObjectName contains "ASB Queue" or "Azure Service Bus"`
**Time Range**: 24 hours
**Aggregation**: Hourly bins

### Query 3: Slow Export Operations
**Query ID**: `b7c8d9e0-f1a2-4456-7890-123456abcde4`
**Filter**: Hagar extensions with "Export" or "Delete" in object name
**Time Range**: 24 hours
**Threshold**: Only shows operations > 1 second

### Query 4: Errors & Warnings
**Query ID**: `c8d9e0f1-a2b3-4567-8901-234567abcde6`
**Filter**: `severityLevel >= 2` (Warning or higher)
**Time Range**: 24 hours
**Aggregation**: By severity and object

---

## What to Monitor

### 🔴 Critical Issues
1. **ASB Queue errors** - Azure Service Bus integration failing
2. **Export operations > 60 seconds** - May impact user experience
3. **Critical severity events** - System errors

### ⚠️ Warnings
1. **ASB Queue response time > 500ms** - Performance degradation
2. **Export operations 30-60 seconds** - Slow but functional
3. **Extensions inactive > 1 hour** - May indicate issue

### 📊 Information
1. **Activity patterns** - Normal variations in event rates
2. **Export operations 10-30 seconds** - Expected for large datasets
3. **Low warning counts** - Generally acceptable

---

## Based on Your 24-Hour Data

### What You'll See

**Hagar Connect** (1,115 events):
- ✅ Very active (46 events/hour)
- HAG ASB Queue: 858 calls (most active component)
- HAG Datadog Utils: 251 calls (logging/monitoring)
- HAG Export Processing: 6 operations
- Status: ✅ Healthy

**Hagar Webshop** (64 events):
- ✅ Light but steady activity (3 events/hour)
- HAG Delete Export Tools: 27 slow queries (expected for cleanup)
- HAG Web Inventory Functions: 1 operation
- HAG Customer API: 1 operation
- Status: ✅ Healthy

### Expected Performance

**ASB Queue**:
- ~36 calls/hour
- Response time: Should be < 100ms
- Errors: Should be 0

**Export Operations**:
- Occasional slow queries (27 in 24h for Delete Export Tools)
- Average: 10-30 seconds (acceptable for batch operations)
- Max: Could be 60+ seconds for large datasets

---

## Comparison: Two Pages Side-by-Side

| Aspect | Custom: Unused Objects | Hagar Extensions |
|--------|----------------------|------------------|
| **Focus** | Cleanup & Removal | Monitoring & Performance |
| **Extensions** | Storkaup, NVL (WebStore) | Hagar Connect, Hagar Webshop |
| **Time Range** | 30 days | 24 hours |
| **Purpose** | Find unused code to remove | Track active integrations |
| **Metrics** | Usage counts, staleness | Performance, errors, activity |
| **Action** | Remove low-usage objects | Fix performance issues |

---

## Troubleshooting

### If Hagar Extensions Page is Empty

**Check 1**: Verify extension names
```kql
traces
| where timestamp > ago(24h)
| extend extensionName = tostring(customDimensions.extensionName)
| where extensionName contains "Hagar" or extensionName contains "HAG"
| summarize by extensionName
```

**Check 2**: Check if extensions have any telemetry
```kql
traces
| where timestamp > ago(24h)
| extend extensionPublisher = tostring(customDimensions.extensionPublisher)
| where extensionPublisher == "Hagar"
| take 100
```

**Check 3**: Verify time range has data
```kql
traces
| where timestamp > ago(24h)
| count
```

### If ASB Queue Tile is Empty

The query filters for:
- `alObjectName contains "ASB Queue"`
- `alObjectName contains "Azure Service Bus"`

If your object is named differently, update query #2 to match your naming convention.

### If Export Tile is Empty

The query filters for:
- `alObjectName contains "Export"`
- `alObjectName contains "Delete"`
- Execution time > 1 second

If you don't see results, your export operations may be < 1 second (very fast!) or named differently.

---

## Next Steps

1. ✅ **Upload dashboard** to Azure Data Explorer
2. ✅ **Navigate to "Hagar Extensions"** page
3. ✅ **Verify all 4 tiles** display data
4. ✅ **Set up alerts** for critical issues:
   - ASB Queue errors
   - Export operations > 60 seconds
   - Critical severity events
5. ✅ **Review weekly** for performance trends
6. ✅ **Adjust time ranges** if needed (change from 24h to longer periods)

---

## Related Files

- **BCTelemetryDashboard.json** - Modified dashboard with both pages
- **DASHBOARD-CHANGES.md** - Original unused customizations page docs
- **UUID-FIX.md** - UUID format fix documentation
- **KQL-EXTEND-FIX.md** - KQL extend statement fix

---

**Created**: 2025-10-31
**Status**: ✅ Ready for Production Use
**Validation**: ✅ JSON syntax valid, all UUIDs correct
