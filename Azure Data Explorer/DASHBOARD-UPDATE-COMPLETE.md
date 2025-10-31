# BCTelemetry Dashboard Update - HAG Web Service Tile Added ✅

## Summary

Successfully added HAG Web Service monitoring tile and query to `BCTelemetryDashboard.json`.

---

## Changes Made

### 1. New Tile Added
- **ID**: `e9f0a1b2-c3d4-4567-8901-234567bcdef7`
- **Title**: "HAG Web Service API (Page 80107)"
- **Page**: Hagar Extensions (`f4a5b6c7-d8e9-4012-3456-789012abcdef`)
- **Position**: Full width at bottom of page (y: 22)
- **Type**: Table visualization

### 2. New Query Added
- **ID**: `d9e0f1a2-b3c4-4678-9012-345678bcdef8`
- **Filter**: Exact object ID (`alObjectId == "80107"`)
- **Time Range**: Last 24 hours
- **Aggregation**: Hourly bins

---

## What the Tile Shows

The tile displays **hourly metrics** for HAG Web Service API:

| Column | Description |
|--------|-------------|
| **timestamp** | Hour of the day |
| **CallCount** | Number of API calls |
| **AvgMs** | Average response time |
| **P95Ms** | 95th percentile response time |
| **MaxMs** | Slowest call |
| **ErrorCount** | Number of errors |
| **PerformanceStatus** | ✅ Fast / ⚠️ Moderate / 🔴 Slow |
| **HealthStatus** | ✅ Healthy / ⚠️ Inactive / 🔴 Has Errors |
| **LastCall** | Timestamp of last call |

### Status Indicators

**Performance Status**:
- ✅ **Fast (<500ms)** - Good performance
- ⚠️ **Moderate (500ms-1s)** - Acceptable, monitor
- 🔴 **Slow (>1s)** - Performance issue, investigate

**Health Status**:
- ✅ **Healthy** - No errors, actively used
- ⚠️ **Inactive >1h** - No calls in last hour
- 🔴 **Has Errors** - Errors detected, attention required

---

## Query Details

### Filter Fixed
The query uses **exact object ID filtering** to prevent "HAG VAT Posting Setup" from appearing:

```kql
| where alObjectId == "80107"
```

This is more precise than:
```kql
| where alObjectId == "80107" or alObjectName contains "HAG Web Service"
```

### Performance Metrics
Calculates execution time from Business Central telemetry:
```kql
| extend executionTimeMs = toreal(totimespan(customDimensions.serverExecutionTime))/10000
```

### Hourly Aggregation
Groups data by hour for trend analysis:
```kql
by bin(timestamp, 1h)
```

---

## Next Steps

### 1. Upload to Azure Data Explorer
1. Open Azure Data Explorer
2. Navigate to your BCTelemetry Dashboard
3. Click **Edit** → **Upload** or **Import**
4. Select the updated `BCTelemetryDashboard.json`
5. Confirm the upload

### 2. Verify the Tile
1. Navigate to the **"Hagar Extensions"** page
2. Scroll to the bottom
3. You should see **"HAG Web Service API (Page 80107)"** tile
4. Verify it shows data (if no data, check time range and API activity)

### 3. Monitor API Health
Set up alerts for:
- 🔴 **Critical**: Error count > 0, Average response time > 1s
- ⚠️ **Warning**: Average response time > 500ms, Inactive > 2 hours

---

## Hagar Extensions Page Layout

Your "Hagar Extensions" page now has **5 tiles**:

```
┌─────────────────────────────────────────────────┐
│  1. Hagar Extensions Activity Overview          │
│     (Full width, top)                           │
└─────────────────────────────────────────────────┘

┌────────────────────────┬────────────────────────┐
│  2. ASB Queue          │  3. Export Processing  │
│     Performance        │     & Slow Operations  │
│     (Left, middle)     │     (Right, middle)    │
└────────────────────────┴────────────────────────┘

┌─────────────────────────────────────────────────┐
│  4. Hagar Extensions Errors & Warnings          │
│     (Full width, bottom-middle)                 │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  5. HAG Web Service API (Page 80107)    ✅ NEW! │
│     (Full width, bottom)                        │
└─────────────────────────────────────────────────┘
```

---

## Tracking Individual Procedures

The current tile tracks **Page 80107 as a whole**. To track individual procedures like `GetTransactions` and `GetInvoice`, you need to add custom telemetry to your AL code.

### Implementation Guide
See these files for complete instructions:
- **PROCEDURE-TRACKING-SUMMARY.md** - Complete implementation guide
- **HAGWebService-AddProcedureTelemetry.al** - AL code examples
- **HAGWebService-ProcedureTracking.kql** - Diagnostic queries

### Quick Steps
1. Add `LogProcedureCall` helper to page 80107
2. Add telemetry calls to each procedure you want to track
3. Deploy and test
4. Run procedure tracking queries to verify

---

## Additional Analysis Queries

For deeper analysis, use:
- **HAGWebService-Analysis.kql** - 10 detailed analysis queries
- **HAGWebService-ProcedureTracking.kql** - 8 diagnostic queries

---

## Verification Checklist

- ✅ Tile added with ID `e9f0a1b2-c3d4-4567-8901-234567bcdef7`
- ✅ Query added with ID `d9e0f1a2-b3c4-4678-9012-345678bcdef8`
- ✅ Tile references correct query ID
- ✅ Tile assigned to Hagar Extensions page
- ✅ Query uses exact object ID filter (fixes "HAG VAT Posting Setup" issue)
- ✅ JSON structure validated

---

## Files Reference

| File | Purpose |
|------|---------|
| `BCTelemetryDashboard.json` | **Updated dashboard** - Upload this to ADE |
| `HAG-WEB-SERVICE-DASHBOARD-UPDATE.json` | Tile and query JSON (reference) |
| `HAG-WEB-SERVICE-TILE-ADDED.md` | Implementation documentation |
| `HAGWebService-Analysis.kql` | 10 analysis queries |
| `HAGWebService-ProcedureTracking.kql` | 8 diagnostic queries |
| `HAGWebService-AddProcedureTelemetry.al` | AL code for procedure tracking |
| `PROCEDURE-TRACKING-SUMMARY.md` | Procedure tracking guide |

---

**Status**: ✅ Complete - Ready to upload to Azure Data Explorer
**Location**: `C:\AL\BCTelemetry\Azure Data Explorer\BCTelemetryDashboard.json`
**Date**: 2025-10-31
