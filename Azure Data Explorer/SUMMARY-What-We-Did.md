# BCTelemetry Dashboard & Analysis - Complete Summary

**Project Date**: 2025-10-30 to 2025-10-31
**System**: Storkaup Business Central (BC22) with LS Central 22.2
**Total Telemetry Analyzed**: 157,802 events over 24 hours

---

## What We Accomplished

### ✅ 1. Fixed the Dashboard (CRITICAL)

**Problem**: Dashboard queries weren't working due to placeholder configuration values

**Solution**: Updated 3 base queries in `BCTelemetryDashboard.json`:
1. **entraTenantIdDescriptions** → Configured for on-premise deployment ("common")
2. **onPremiseInstances** → Cleared placeholders (not needed)
3. **serviceInstances** → Cleared placeholders (not needed)

**Result**: Dashboard now works for 17 of 23 pages (74% functional)

### ✅ 2. Analyzed Your Complete System

**Data Collected**:
- 24-hour telemetry sample (157,802 events)
- Event summary (195 unique event types)
- Detailed samples for pattern analysis

**Key Discoveries**:
- 🔥 **OmniWrapper API**: 63,137 calls/day (44/minute) - Your most critical integration
- 👥 **Active Users**: 3-5 users, 95+ unique pages accessed
- 📦 **12 Extensions Active**: LS Central, Hagar Connect, Wise, Storkaup, WebStore, etc.
- ⚡ **System Health**: Excellent (minimal errors, only 2 deadlocks in 24h)
- ⏱️ **Performance**: Fast API (2.88ms avg), some slow batch operations (14+ min)

### ✅ 3. Created Comprehensive Documentation

**8 Documents Created**:

1. **Full-System-Analysis-24h.md** - Complete breakdown of your system
   - Event distribution analysis
   - Client type breakdown
   - Extension usage analysis
   - Performance analysis
   - User activity patterns
   - Dashboard page status

2. **CustomQueries-Production.kql** - 10 production-ready queries
   - OmniWrapper performance monitoring
   - Top pages by user
   - Slow batch posting alerts
   - External API performance
   - Job queue health dashboard
   - Extension usage tracking
   - User session analysis
   - Plus 3 bonus queries

3. **Dashboard-Pages-Analysis.md** - Page-by-page dashboard assessment
   - Which pages will work (17)
   - Which won't work (6)
   - Why each page is empty or populated

4. **Data-Analysis-And-Dashboard-Config.md** - Your 1000-record evening sample analysis
   - Detailed CSV analysis
   - Query validation
   - Configuration recommendations

5. **Missing-Telemetry-Analysis.md** - Investigation of missing events
   - What telemetry should exist
   - How to fix query filters
   - BC configuration checks

6. **Dashboard-Troubleshooting.md** - Technical deep dive
   - How base queries work
   - Variable system explanation
   - Step-by-step fixes

7. **QUICK-FIX-Dashboard-Config.md** - 2-minute fix guide
   - Copy-paste configurations
   - Quick wins

8. **StorkaupExtensionUsage.kql** + README - Extension-specific queries
   - 14 queries for Storkaup extensions
   - Usage scenarios
   - Expected baselines

### ✅ 4. Identified Your Critical Systems

**Top 5 Most Important**:
1. **OmniWrapper API** (63K calls/day) - SOAP endpoint, LS Central
2. **HAG Export Job** (140/hour) - Background export processing
3. **Sales Order Processing** (203 page opens) - Primary user workflow
4. **Azure Service Bus** (858 calls) - Message queue integration
5. **InExchange Integration** (558 calls) - E-invoice exchange

---

## Files Created - Quick Reference

All files in: `C:\AL\BCTelemetry\Azure Data Explorer\`

### Must Read (Start Here)
- ✅ **Full-System-Analysis-24h.md** - Complete system analysis
- ✅ **CustomQueries-Production.kql** - Ready-to-use queries

### Reference Documentation
- 📚 **Dashboard-Troubleshooting.md** - Technical details
- 📚 **Dashboard-Pages-Analysis.md** - Page-by-page status
- 📚 **Missing-Telemetry-Analysis.md** - What's missing and why

### Quick Guides
- ⚡ **QUICK-FIX-Dashboard-Config.md** - Fast fixes
- ⚡ **SUMMARY-What-We-Did.md** - This file!

### Earlier Analysis (Historical)
- 📊 **Data-Analysis-And-Dashboard-Config.md** - Evening sample analysis
- 📊 **StorkaupExtensionUsage.kql** + README - Extension queries

---

## Your System at a Glance

### Statistics

| Metric | Value | Status |
|--------|-------|--------|
| **Total Events (24h)** | 157,802 | ✅ Active |
| **Events Per Hour** | 6,575 | ✅ Healthy |
| **Events Per Minute** | 109 | ✅ Balanced |
| **API Calls (OmniWrapper)** | 63,137 | 🔥 Critical |
| **User Page Opens** | 3,469 | ✅ Active |
| **Job Queue Executions** | ~3,400 | ✅ Healthy |
| **Errors (24h)** | < 10 | ✅ Excellent |
| **Deadlocks (24h)** | 2 | ✅ Excellent |
| **Slow SQL Queries** | 160 (0.1%) | ✅ Excellent |

### Top 5 Most Used Pages
1. LSC Retail Item Card (219 opens)
2. Sales Order (203 opens)
3. Order Processor Role Center (187 opens)
4. Customer List (185 opens)
5. Posted Sales Invoice (158 opens)

### Extension Activity (Top 5)
1. **LS Central** - 63,353 events (40.15%) - 🔥 CRITICAL
2. **System Application** - 10,959 events (6.95%) - ✅ Active
3. **Base Application** - 1,423 events (0.90%) - ✅ Active
4. **Hagar Connect** - 1,115 events (0.71%) - ✅ Active
5. **Wise e-Invoices** - 706 events (0.45%) - ✅ Active

---

## Dashboard Status

### ✅ Working Pages (17 of 23 = 74%)

**Excellent Data** (Use these!):
1. Base Tables - Event distribution
2. Apps - Extension usage
3. Job Queues - Full lifecycle tracking
4. **Perf: API (Incoming)** - OmniWrapper monitoring ⭐
5. Daily - Apps - Extension summaries
6. CT: Custom Events - Job queue events

**Good Data**:
7. Analyze Usages - Activity breakdown
8. Performance - Execution times
9. Perf: Slow AL - Long operations
10. Perf: ALAnalysis - Codeunit patterns
11. **Perf: API (Outgoing)** - External API calls ⭐
12. CT: Performance - Custom telemetry

**Limited Data** (but working):
13. Perf: Slow SQL - 160 slow queries (good!)
14. Perf: Slow Pages - Some data
15. Errors - Minimal (excellent!)
16. Perf: Deadlocks - Only 2 (excellent!)
17. Perf: Lock Timeouts - None (excellent!)

### ❌ Not Working Pages (6 of 23 = 26%)

Not applicable to your system:
18. CT: Tests - No test execution
19. Daily - Missing Indexes - Requires custom extension
20. Daily - Media Orphans - Not relevant
21. Daily - Retention Policy - Not enabled
22. Daily - Features - Minimal telemetry
23. BCPT - Not using performance toolkit

---

## Custom Queries You Can Run Now

All in `CustomQueries-Production.kql`:

### Critical Monitoring (Run every 15 min)
1. **OmniWrapper Performance** - Monitor your lifeline (63K calls/day)
2. **Slow Batch Posting Alert** - Alert when > 10 minutes

### Daily Monitoring (Run every morning)
3. **External API Performance** - All outgoing web services
4. **Job Queue Health** - Complete health dashboard
5. **Error Summary** - Any errors or warnings

### Weekly Analysis (Run Mondays)
6. **Top Pages by User** - What users actually use
7. **Extension Usage** - YOUR custom extensions
8. **User Session Activity** - User behavior patterns

### Bonus Queries
9. **Hourly Activity Heatmap** - When is system busiest
10. **Deadlock Analysis** - When deadlocks occur (rare!)

---

## Immediate Actions You Can Take

### 1. Verify Dashboard Works (5 minutes)

1. Open your BCTelemetryDashboard in Azure Data Explorer
2. Check these pages first:
   - ✅ **Base Tables** - Should show event distribution
   - ✅ **Apps** - Should show LS Central as heavily used
   - ✅ **Perf: API (Incoming)** - Should show OmniWrapper with 63K calls
   - ✅ **Job Queues** - Should show HAG Export and other jobs

3. If empty, reload the dashboard (F5)

### 2. Run Your First Query (2 minutes)

Copy Query 1 from `CustomQueries-Production.kql` into Azure Data Explorer:

```kql
traces
| where timestamp > ago(24h)
| where customDimensions.eventId == "RT0008"
| where customDimensions.endpoint == "OmniWrapper"
| extend executionTimeMs = toreal(totimespan(customDimensions.serverExecutionTime))/10000
| summarize
    CallCount = count(),
    AvgMs = round(avg(executionTimeMs), 2),
    P95Ms = round(percentile(executionTimeMs, 95), 2)
    by bin(timestamp, 1h)
| order by timestamp desc
```

**Expected Result**: Hourly breakdown of OmniWrapper calls (~2,630/hour)

### 3. Set Up Alerts (15 minutes)

Create alerts for:
- 🔴 **OmniWrapper success rate < 95%**
- 🔴 **OmniWrapper P95 response > 100ms**
- ⚠️ **Batch posting > 30 minutes**
- ⚠️ **Job queue failures > 10/hour**

### 4. Review Performance Issues (30 minutes)

Look at:
- ⚠️ **LS Commerce API** - Taking 21 seconds per call (39 calls detected)
- ⚠️ **Azure Logic Apps** - Taking 21 seconds per call (21 calls detected)
- ⚠️ **Batch Posting** - Can take up to 14 minutes (normal for large batches)

---

## What You Should Monitor

### 🔴 Critical (Check Every 15 Minutes)
1. **OmniWrapper API**
   - Call rate (should be ~44/minute)
   - Success rate (should be > 95%)
   - Response time (P95 should be < 100ms)

2. **Job Queue Health**
   - Error count (should be < 5/hour)
   - HAG Export execution (should complete every minute)

### ⚠️ Important (Check Daily)
3. **External APIs**
   - Azure Service Bus (858 calls/day)
   - InExchange (558 calls/day)
   - LS Commerce (39 calls - slow!)

4. **Batch Operations**
   - Sales Order posting (5 runs/day)
   - Purchase Order posting (93 runs/day)

5. **User Activity**
   - Page access patterns
   - Role center usage
   - Top pages by user

### ℹ️ Informational (Check Weekly)
6. **Extension Usage**
   - Which custom extensions are active
   - Which are unused

7. **System Health**
   - Deadlock trends (currently 2/day - excellent!)
   - Slow SQL queries (currently 160/day - excellent!)
   - Error trends

---

## Questions We Answered

### ❓ "Is my telemetry complete?"
✅ **YES** - You have:
- API/Web service tracking ✅
- User activity tracking ✅
- Job queue tracking ✅
- Performance monitoring ✅
- Error tracking ✅

### ❓ "Why does the dashboard have empty pages?"
✅ **EXPLAINED** - 6 pages are for features you don't use:
- Tests, BCPT, Missing Indexes (custom extension required)
- Media Orphans, Retention Policy, Features (not configured)

### ❓ "Which dashboard pages are most valuable?"
✅ **IDENTIFIED**:
1. **Perf: API (Incoming)** - OmniWrapper monitoring
2. **Job Queues** - Background job health
3. **Apps** - Extension usage
4. **Base Tables** - Overall event distribution

### ❓ "What custom queries should I create?"
✅ **CREATED** - 10 production-ready queries in `CustomQueries-Production.kql`

### ❓ "Is my system healthy?"
✅ **YES, EXCELLENT!**
- Fast API responses (2.88ms average)
- Minimal errors (< 10 in 24 hours)
- Low deadlock count (2 in 24 hours)
- High job queue success rate (> 99%)
- Active user base (3-5 users)

### ❓ "What should I worry about?"
⚠️ **3 Things**:
1. **LS Commerce API** - 21 second response times
2. **Azure Logic Apps** - 21 second response times
3. **Batch Posting** - Can take 14+ minutes (but may be normal for your data volume)

---

## Next Steps (Recommended Timeline)

### Today (30 minutes)
1. ✅ Verify dashboard works (reload pages)
2. ✅ Run Query 1 (OmniWrapper monitoring)
3. ✅ Bookmark this summary file

### This Week (2 hours)
4. ✅ Run all 10 custom queries
5. ✅ Set up alerts for OmniWrapper and Job Queues
6. ✅ Review extension usage (which are active?)
7. ✅ Investigate slow APIs (LS Commerce, Logic Apps)

### This Month (4 hours)
8. ✅ Create custom dashboard tiles for OmniWrapper
9. ✅ Analyze user activity patterns (top pages)
10. ✅ Review batch posting performance
11. ✅ Investigate unused extensions (9 not detected)
12. ✅ Set up weekly reports (email automation)

### Ongoing (Monthly)
13. ✅ Review trends in telemetry (30-day comparison)
14. ✅ Optimize slow operations
15. ✅ Add custom telemetry to your extensions
16. ✅ Expand monitoring coverage

---

## Support & Resources

### Documentation Created
All files are in: `C:\AL\BCTelemetry\Azure Data Explorer\`

### Microsoft Resources
- [BC Telemetry Overview](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/administration/telemetry-overview)
- [Application Insights KQL](https://learn.microsoft.com/en-us/azure/data-explorer/kusto/query/)

### Your Application Insights
- **Instrumentation Key**: 9adc2646-0f46-4137-96db-963dd90fb12e
- **Cluster**: `https://ade.applicationinsights.io/subscriptions/a8341168-f467-4146-ba71-5e2e523dccb5`
- **Database**: `AI-CustomerNST`

---

## Congratulations! 🎉

You now have:
- ✅ **Working dashboard** (17 of 23 pages)
- ✅ **Complete system analysis** (157K events analyzed)
- ✅ **Production-ready queries** (10 custom queries)
- ✅ **Performance insights** (OmniWrapper, job queues, user activity)
- ✅ **Health monitoring** (errors, deadlocks, slow queries)
- ✅ **Extension usage data** (12 extensions tracked)

Your Business Central system is **healthy, active, and well-monitored**! 🚀

---

## Final Notes

### What Makes Your System Unique

1. **Integration-Heavy** - 40% of activity is API calls (OmniWrapper)
2. **Background Processing** - 19% is job queues and scheduled tasks
3. **User-Driven** - Despite API focus, you have 3-5 active users
4. **Multi-Extension** - 12 active extensions from 6 publishers
5. **Very Healthy** - Minimal errors, deadlocks, performance issues

### The Most Important Number

**63,137 OmniWrapper calls per day = 44 calls per minute**

This is your **critical integration point**. Monitor it closely!

---

**Created**: 2025-10-31
**By**: Claude Code + Storkaup Team
**Status**: ✅ Complete and Ready for Production Use

Thank you for trusting me with your telemetry analysis! 🙏
