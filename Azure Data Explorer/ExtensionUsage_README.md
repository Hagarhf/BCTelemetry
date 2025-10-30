# Storkaup Extension Usage Queries

This file documents the KQL queries in `StorkaupExtensionUsage.kql` for analyzing Business Central extension usage via Application Insights telemetry.

## Quick Start

### Priority Queries (Run These First)

1. **Query 1**: Extension Usage Summary → Get baseline of all extensions
2. **Query 2**: Unused Extensions → Identify zero-activity extensions
3. **Query 9**: Critical Extensions Activity → Deep dive into core extensions

### File Location
`C:\AL\BCTelemetry\Azure Data Explorer\StorkaupExtensionUsage.kql`

## Query Reference

### Extension Usage Analysis

| Query | Name | Purpose | Time Range |
|-------|------|---------|------------|
| 1 | Extension Usage Summary | Overall activity count, users, last usage | 30 days |
| 2 | Completely Unused Extensions | Extensions with zero telemetry | 30 days |
| 9 | Critical Storkaup Extensions | Detailed activity for core extensions | 30 days |
| 10 | User Adoption by Extension | Which users use which extensions | 30 days |
| 14 | Feature Adoption Trend | Adoption over time (chart) | 90 days |

### Page Usage Analysis

| Query | Name | Purpose | Time Range |
|-------|------|---------|------------|
| 3 | Page Usage by Extension | Most/least used pages | 30 days |
| 11 | Page Usage Heatmap | Top 100 page/extension combinations | 30 days |
| 12 | Slow Pages Report | Pages taking > 2 seconds | 7 days |

### Codeunit & Job Queue

| Query | Name | Purpose | Time Range |
|-------|------|---------|------------|
| 4 | Codeunit Execution Frequency | Execution count and performance | 30 days |
| 6 | Job Queue Execution | Scheduled task monitoring | 30 days |

### Integration & API

| Query | Name | Purpose | Time Range |
|-------|------|---------|------------|
| 5 | Web Service / API Usage | API endpoint calls and success rates | 30 days |
| 13 | Integration Point Activity | External system integration tracking | 30 days |

### Performance & Errors

| Query | Name | Purpose | Time Range |
|-------|------|---------|------------|
| 7 | Extension Performance Impact | P95/P99 latency by extension | 7 days |
| 8 | Error Rate by Extension | Error counts and unique errors | 30 days |

## Usage Scenarios

### Scenario 1: Identify Unused Extensions

**Goal**: Find extensions with zero activity to consider for removal

**Steps**:
1. Run **Query 2** (Unused Extensions)
2. For each unused extension, run **Query 3** (Page Usage) filtered to that extension
3. Run **Query 4** (Codeunit Execution) filtered to that extension
4. Verify it's not a scheduled job with **Query 6**

**Example Result**:
```
UnusedExtension
NVL_COLineStatus
PO_AutoInvoicing
```

**Action**: Check if these are seasonal or scheduled jobs before considering removal.

### Scenario 2: Performance Optimization

**Goal**: Find and optimize slow extensions

**Steps**:
1. Run **Query 7** (Extension Performance)
2. Identify extensions with P95 > 2000ms
3. Run **Query 12** (Slow Pages) for those extensions
4. Run **Query 4** (Codeunit Execution) to find slow codeunits

**Example Result**:
```
extensionName       | P95ExecutionTimeMs | PerformanceRating
WebStore           | 3500               | ❌ Slow (> 2000ms)
Datadwell          | 2800               | ❌ Slow (> 2000ms)
```

**Action**: Optimize WebStore and Datadwell integrations.

### Scenario 3: Validate Critical Extensions

**Goal**: Ensure core business extensions are actively used

**Steps**:
1. Run **Query 9** (Critical Extensions)
2. Verify all critical extensions have recent activity
3. Check error rates are acceptable (< 5%)

**Expected Result**:
```
extensionName       | TotalActivities | UniqueUsers | ErrorRate | DaysSinceLastUse
Storkaup           | 15,000          | 25          | 0.5%      | 0
OrderProcess       | 8,000           | 20          | 1.2%      | 0
WebStore           | 5,000           | 15          | 2.1%      | 0
```

**Action**: If any critical extension shows `DaysSinceLastUse > 1`, investigate immediately.

### Scenario 4: Monitor Integration Health

**Goal**: Ensure external integrations are working

**Steps**:
1. Run **Query 13** (Integration Activity)
2. Run **Query 5** (API Usage) for integration extensions
3. Check success rates are > 95%

**Example for Datadwell**:
```
endpoint                    | CallCount | SuccessRate | ErrorCount
/api/datadwell/search      | 450       | 98.2%       | 8
```

**Action**: Investigate 8 errors in Datadwell API calls.

### Scenario 5: User Adoption Analysis

**Goal**: Track which users are adopting new features

**Steps**:
1. Run **Query 14** (Feature Adoption Trend) for new extensions
2. Run **Query 10** (User Adoption) to see per-user usage
3. Identify power users vs. non-adopters

**Action**: Target training for non-adopters.

## Expected Baseline Metrics

Based on Storkaup architecture, expected activity levels:

### Heavily Used (1000+ activities/month)
- **Storkaup** - Core app, all users
- **OrderProcess** - Multiple PO creations daily
- **SalesReleaseCheck** - Every order release

### Actively Used (100-1000 activities/month)
- **WebStore** - Web order imports
- **CustomerCreditCheck** - Order validation
- **LiquorLicense** - Alcohol sale validation
- **NationalRegistry** - Customer creation events

### Moderately Used (10-100 activities/month)
- **Datadwell** - Scheduled sync jobs
- **StorkaupAddons** - Background Adfong sync
- **NVLJobQueueEntriesNeverStop** - Job monitoring

### Rarely Used (< 10 activities/month)
- **ItemBatchCreation** - Occasional bulk imports
- **StorkaupReport** - Month-end reports
- **CustomerPortal** - Customer-initiated

## Alerting Recommendations

### Critical Alerts (Immediate Response)

Set up alerts for:
1. **Zero Activity on Critical Extensions** (Query 9)
   - Threshold: No activity in 24 hours
   - Extensions: Storkaup, OrderProcess, WebStore, SalesReleaseCheck

2. **High Error Rate** (Query 8)
   - Threshold: Error rate > 5%
   - Action: Investigate logs

3. **API Failure Rate** (Query 5)
   - Threshold: Success rate < 90%
   - Extensions: WebStore, Datadwell, CustomerPortal

### Warning Alerts (Daily Review)

1. **Performance Degradation** (Query 7)
   - Threshold: P95 execution time increased by 50%

2. **Slow Pages** (Query 12)
   - Threshold: Any page > 5 seconds

3. **Job Queue Failures** (Query 6)
   - Threshold: > 2 failures for same job

## Dashboard Setup

### Recommended Dashboard Layout

**Row 1: Executive Summary**
- Query 1: Extension Usage Summary (Table)
- Query 9: Critical Extensions (Table)

**Row 2: Usage Trends**
- Query 14: Feature Adoption (Line Chart)
- Query 10: User Adoption (Bar Chart)

**Row 3: Performance**
- Query 7: Performance Impact (Bar Chart)
- Query 12: Slow Pages (Table)

**Row 4: Health**
- Query 8: Error Rates (Pie Chart)
- Query 5: API Success Rates (Gauge)

### Auto-Refresh Settings
- Executive Summary: 15 minutes
- Trends: 1 hour
- Performance: 5 minutes
- Health: 5 minutes

## Customization Guide

### Adjusting Time Ranges

All queries use `ago(Xd)` syntax:
- `ago(1d)` = Last 24 hours
- `ago(7d)` = Last 7 days
- `ago(30d)` = Last 30 days
- `ago(90d)` = Last 90 days

Example: To analyze last 7 days instead of 30:
```kql
// Before
| where timestamp > ago(30d)

// After
| where timestamp > ago(7d)
```

### Filtering to Specific Extensions

Many queries can be filtered to specific extensions:

```kql
// Add after the where timestamp clause
| where extensionName in ("Storkaup", "OrderProcess", "WebStore")
```

### Excluding Test Data

If you have test environments, exclude them:

```kql
// Add to any query
| where cloud_RoleName != "BC-TEST"  // Adjust to your test environment name
```

## Troubleshooting

### No Data Returned

**Possible Causes**:
1. Time range too narrow → Try `ago(90d)`
2. Extension name mismatch → Run Query 1 to see actual names
3. Telemetry not configured → Verify `applicationInsightsConnectionString` in app.json
4. Event ID mismatch → Check actual eventId values in your data

**Debug Query**:
```kql
traces
| where timestamp > ago(1h)
| take 10
| project timestamp, message, customDimensions
```

### Performance Issues

If queries are slow:
1. Reduce time range (e.g., `ago(7d)` instead of `ago(90d)`)
2. Add filters early in query (before summarize)
3. Use `take` to limit results for testing

### Incorrect Counts

Verify event IDs match your telemetry:
- RT0004 = Method execution
- RT0005 = Page opened
- RT0008 = Web service called
- RT0012 = Job queue entry

Run this to see your actual event IDs:
```kql
traces
| where timestamp > ago(1d)
| extend eventId = tostring(customDimensions.eventId)
| summarize count() by eventId
| order by count_ desc
```

## Related Files

- `DiscoveryQueries.kql` - Tenant and instance discovery
- `PropertyExplorer.kql` - Explore customDimensions structure
- `BCTelemetryDashboard.json` - Main dashboard definition

## Maintenance

### Weekly Tasks
- Run Query 1 (Extension Usage Summary)
- Review Query 2 (Unused Extensions)
- Check Query 8 (Error Rates)

### Monthly Tasks
- Comprehensive review of Query 9 (Critical Extensions)
- Performance baseline update (Query 7)
- User adoption analysis (Query 10)

### Quarterly Tasks
- Review unused extensions for deprecation
- Update critical extensions list in queries
- Adjust thresholds based on trends

## Support

For questions about:
- **KQL Syntax**: [Kusto Query Language Documentation](https://docs.microsoft.com/en-us/azure/data-explorer/kusto/query/)
- **BC Telemetry**: [Business Central Telemetry Documentation](https://docs.microsoft.com/en-us/dynamics365/business-central/dev-itpro/administration/telemetry-overview)
- **Storkaup Extensions**: See `/docs/extensions/` in repository

---

**Last Updated**: 2025-10-30
**Version**: 1.0
**Author**: Claude Code
