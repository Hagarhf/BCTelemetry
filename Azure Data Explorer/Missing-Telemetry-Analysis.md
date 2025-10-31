# Missing Telemetry Analysis

**Date**: 2025-10-30
**Issue**: Dashboard appears API-only, but system has user interactions

## Current Telemetry Snapshot

### What IS Being Captured ✅

From your 1000-record sample (all from 10/30/2025, ~9:40-9:48 PM):

| Event Type | Count | What It Tracks |
|------------|-------|----------------|
| RT0004 | 876 | Authorization Succeeded (Open Company) |
| RT0008 | 824 | Web service called (SOAP) - OmniWrapper |
| LC0043 | 54 | Task completed |
| LC0040 | 54 | Task created |
| AL0000E24 | 54 | Job queue entry enqueued |
| LC0042 | 42 | Task removed |
| AL0000E26 | 42 | Job queue entry finished |
| AL0000E25 | 42 | Job queue entry started |
| RT0019 | 8 | Company opened |
| RT0006 | 4 | Session started |

**Client Types Detected**:
- WebServiceClient (majority - OmniWrapper SOAP calls)
- Background (job queue entries)

### What is MISSING ❌

Critical telemetry events that should exist if users are active:

#### User Interaction Events (ALL MISSING)

| Event ID | Description | Why Important |
|----------|-------------|---------------|
| **RT0012** | Page opened | Tracks which pages users visit |
| **RT0011** | Page closed | User session patterns |
| **RT0005** | Long running operation | Performance issues |
| **RT0030** | Outgoing web service calls | API integrations |
| **RT0002** | Session created | User login tracking |
| **RT0003** | Session stopped | Session duration |

#### Report & Document Events (MISSING)

| Event ID | Description |
|----------|-------------|
| **RT0006** | Report rendering started |
| **RT0007** | Report rendering finished |
| **RT0013** | Report started |
| **RT0014** | Report finished |

#### Database Performance Events (MISSING)

| Event ID | Description | Dashboard Impact |
|----------|-------------|------------------|
| **RT0005** | Long running SQL queries | Perf: Slow SQL (empty) |
| **RT0020** | Deadlock detected | Perf: Deadlocks (empty) |
| **RT0010** | SQL query timeout | Perf: Lock Timeouts (empty) |

#### Custom Extension Events (MISSING)

| Event Type | Description |
|------------|-------------|
| **AL0000...** (custom) | Custom telemetry from your extensions |
| **ALIFCTLM0001** | Missing index recommendations |
| **ALIFCTLM0002** | Custom performance measurements |

## Time Range Issue

**Critical Finding**: Your CSV contains only ~8 minutes of data (9:40 PM - 9:48 PM)

**Time Range**: 10/30/2025, 9:40 PM - 9:48 PM
**Duration**: Approximately 8 minutes
**Sample Size**: 1000 events

### Why This Matters

An 8-minute sample during evening hours:
- ❌ May miss business hours user activity (9 AM - 5 PM)
- ❌ May miss peak usage times
- ❌ Only captures background processes (job queues, web services)
- ✅ Good for API/integration monitoring
- ⚠️ NOT representative of full system usage

## Possible Reasons for Missing Telemetry

### 1. Application Insights Query Filters

**Most Likely**: Your query to export the CSV may have filters limiting results.

**Check your query for**:
```kql
// Bad - filters that exclude user activity
traces
| where timestamp > ago(1h)  // Only last hour
| where eventId in ("RT0004", "RT0008", "LC0043", ...)  // Only specific events
| where clientType == "WebServiceClient"  // Only API calls
| take 1000  // Only 1000 records

// Good - get all telemetry
traces
| where timestamp > ago(24h)  // Full day
// No eventId filter
// No clientType filter
| take 10000  // Larger sample
```

### 2. Telemetry Configuration in Business Central

**Check BC Server Configuration**:

Your BC server may not be configured to send all telemetry events.

**Location**: BC Server Instance settings

**Key Settings to Verify**:
```
Application Insights Connection String: [Should be set]
Application Insights Instrumentation Key: 9adc2646-0f46-4137-96db-963dd90fb12e

// Telemetry settings
Enable Telemetry: Yes
Log Level: Information (or Verbose for more detail)
```

### 3. Time of Data Collection

**Your Sample**: 9:40-9:48 PM (Evening)

**Questions**:
- Are users typically working at 9:40 PM?
- Is this after business hours?
- Were any users logged in during this time?

**Action**: Pull data from business hours (e.g., 10 AM - 2 PM)

### 4. Missing Event Categories in Application Insights

Some event types require specific BC configuration:

#### Page Telemetry (RT0012)
**Requires**:
- User sessions (not web service)
- Page opens/closes
- May be disabled in BC configuration

#### Report Telemetry (RT0006, RT0007)
**Requires**:
- Report execution
- May be disabled or filtered

#### Long Running Operations (RT0005)
**Requires**:
- Operations exceeding threshold (default: 1000ms)
- Your system is very fast (1-2ms), so may not trigger

#### Custom Extension Telemetry
**Requires**:
- Extensions to explicitly log telemetry
- Your custom extensions may not be instrumented

## How to Diagnose

### Step 1: Check Application Insights Directly

Run this query in Application Insights / Azure Data Explorer:

```kql
// Get ALL event types from last 24 hours
traces
| where timestamp > ago(24h)
| extend eventId = tostring(customDimensions.eventId)
| summarize Count = count() by eventId
| order by Count desc
```

**Expected Results**:
- If you see RT0012, RT0011, etc. → Query filter issue
- If you only see RT0004, RT0008, LC*, AL* → Telemetry configuration issue

### Step 2: Check Business Hours Activity

```kql
// Get events during business hours
traces
| where timestamp > ago(7d)
| extend hour = datetime_part("hour", timestamp)
| where hour >= 9 and hour <= 17  // Business hours
| extend eventId = tostring(customDimensions.eventId)
| summarize Count = count() by eventId, hour
| order by hour, Count desc
```

**Expected Results**:
- Should see more diverse event types during business hours
- Should see user sessions, page opens, reports

### Step 3: Check for User Sessions

```kql
// Find user sessions (not web service or background)
traces
| where timestamp > ago(24h)
| extend clientType = tostring(customDimensions.clientType)
| where clientType !in ("WebServiceClient", "Background")
| summarize Count = count(), ClientTypes = make_set(clientType)
| project Count, ClientTypes
```

**Expected Results**:
- If Count > 0: User sessions exist, query filter issue
- If Count = 0: No user telemetry being captured

### Step 4: Check Telemetry Coverage

```kql
// Check telemetry coverage over 24 hours
traces
| where timestamp > ago(24h)
| summarize EventCount = count() by bin(timestamp, 1h)
| order by timestamp desc
```

**Expected Results**:
- Should see activity during business hours
- Pattern should match business operations
- Your sample shows only 9:40-9:48 PM

## What You Should See in a Healthy System

For a Business Central system with user activity, typical 24-hour breakdown:

| Event Category | % of Total | Example Count (10K events) |
|----------------|------------|----------------------------|
| Authorization (RT0004) | 30-40% | 3,000-4,000 |
| Page Opens (RT0012) | 20-30% | 2,000-3,000 |
| Web Services (RT0008) | 10-20% | 1,000-2,000 |
| Reports (RT0006, RT0007) | 5-10% | 500-1,000 |
| Job Queues (AL0000E*) | 5-10% | 500-1,000 |
| Sessions (RT0002, RT0003) | 5-10% | 500-1,000 |
| Other | 10-15% | 1,000-1,500 |

**Your Current Distribution**:
| Event Category | % of Total |
|----------------|------------|
| Authorization (RT0004) | 87.6% ⚠️ |
| Web Services (RT0008) | 82.4% ⚠️ |
| Job Queues | 15% ✅ |
| **Page Opens (RT0012)** | **0%** ❌ |
| **Reports** | **0%** ❌ |
| **User Sessions** | **0%** ❌ |

## Recommended Actions

### Immediate: Expand Your Query

**Replace your current CSV export query with**:

```kql
traces
| union pageViews
| where timestamp > ago(24h)
| where customDimensions.aadTenantId == "common"
| where customDimensions.companyName == "Stórkaup ehf"
// NO eventId filter - get everything
// NO clientType filter - get all client types
| extend eventId = tostring(customDimensions.eventId)
| extend clientType = tostring(customDimensions.clientType)
| extend alObjectType = tostring(customDimensions.alObjectType)
| project
    timestamp,
    eventId,
    clientType,
    alObjectType,
    message,
    customDimensions
| order by timestamp desc
| take 10000  // Larger sample
```

**Export this** to a new CSV and share - I'll analyze it!

### Short-Term: Verify BC Configuration

**Check BC Server Settings**:

1. Open BC Administration Shell
2. Run:
```powershell
Get-NAVServerConfiguration -ServerInstance BC220 -KeyName "ApplicationInsightsInstrumentationKey"
Get-NAVServerConfiguration -ServerInstance BC220 -KeyName "ApplicationInsightsConnectionString"
```

3. Verify settings are correct

4. Check if any telemetry is disabled:
```powershell
Get-NAVServerConfiguration -ServerInstance BC220 | Select-String -Pattern "Telemetry"
```

### Medium-Term: Enable Missing Telemetry

If page/report telemetry is missing, you may need to enable it:

**In BC Server Configuration**:
```
Enable Page Telemetry: Yes
Enable Report Telemetry: Yes
Telemetry Log Level: Information (or Verbose)
```

Restart BC service after changes.

### Long-Term: Custom Extension Telemetry

For your custom extensions (Storkaup, OrderProcess, WebStore, etc.):

**Add telemetry in your AL code**:

```al
codeunit 50000 "My Custom Codeunit"
{
    var
        Telemetry: Codeunit "Telemetry";

    procedure MyProcedure()
    var
        StartTime: DateTime;
        Dimensions: Dictionary of [Text, Text];
    begin
        StartTime := CurrentDateTime;

        // Your code here

        // Log telemetry
        Dimensions.Add('customerId', CustomerId);
        Dimensions.Add('orderCount', Format(OrderCount));

        Telemetry.LogMessage(
            'STORKAUP001',
            'Order processing completed',
            Verbosity::Normal,
            DataClassification::SystemMetadata,
            TelemetryScope::All,
            Dimensions);
    end;
}
```

## Expected Results After Fixes

Once telemetry is properly configured, you should see:

### Dashboard Pages - Updated Status

| Page | Current Status | Expected Status |
|------|----------------|-----------------|
| Base Tables | ✅ Working | ✅ More data |
| Analyze Usages | ⚠️ Limited | ✅ Full data |
| Apps | ✅ Working | ✅ More extensions |
| Errors | ⚠️ Empty | ⚠️ Hopefully still empty! |
| Job Queues | ✅ Working | ✅ Working |
| Performance | ⚠️ Limited | ✅ Full metrics |
| Perf: Slow SQL | ❌ Empty | ⚠️ May have some |
| **Perf: Slow Pages** | ❌ Empty | ✅ **Should populate!** |
| Perf: Slow AL | ⚠️ Limited | ✅ More data |
| Perf: API (Incoming) | ✅ Working | ✅ Working |
| Perf: API (Outgoing) | ❌ Empty | ⚠️ May populate |
| CT: Custom Events | ✅ Limited | ✅ More events |

### New Events You Should See

After expanding your query/fixing config:

- **RT0012**: Page opens (hopefully hundreds per day)
- **RT0011**: Page closes
- **RT0006/RT0007**: Report execution
- **RT0002/RT0003**: User sessions
- **Custom AL0000...**: Your extension telemetry

## How to Share Updated Data

**Option 1: Expanded CSV**

Run the query above and export to:
`C:\AL\BCTelemetry\query_data_full.csv`

Then share that path with me.

**Option 2: Event Summary**

Run this in Azure Data Explorer:

```kql
traces
| where timestamp > ago(24h)
| extend eventId = tostring(customDimensions.eventId)
| extend clientType = tostring(customDimensions.clientType)
| summarize
    Count = count(),
    FirstSeen = min(timestamp),
    LastSeen = max(timestamp)
    by eventId, clientType
| order by Count desc
```

Share the results - I can assess what's missing.

## Summary

**Current Situation**:
- ✅ API/Integration telemetry working perfectly
- ✅ Job queue telemetry working perfectly
- ❌ User interaction telemetry missing
- ❌ Page/Report telemetry missing
- ⚠️ Data sample is only 8 minutes from evening hours

**Most Likely Cause**:
1. CSV export query is filtered (only specific events)
2. Data pulled from non-business hours (9:40 PM)
3. Sample size too small (1000 records from 8 minutes)

**Next Step**:
Run the expanded query above for 24 hours and export to new CSV. This will show the true state of your telemetry!

**Expected Outcome**:
You'll likely find that your system DOES have user telemetry - it's just not in this 8-minute evening sample. The dashboard pages should populate once you have a full 24-hour dataset.
