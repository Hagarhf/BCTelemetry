# CLAUDE.md — BCTelemetry

Azure Data Explorer dashboard and KQL query library for Business Central telemetry monitoring.
Data source: Azure Application Insights (Olis, Storkaup, Bananar).

## Folder structure

```
Azure Data Explorer/
├── dashboard/          # Production KQL queries used in dashboard tiles
├── discovery/          # One-time setup & environment discovery queries
├── diagnostic/         # Troubleshooting & deep-dive queries
├── scripts/            # JS/Python/PowerShell helper utilities
├── ExternalData/       # JSON mapping files (Signals, tenants, instances)
├── docs/               # Setup guides, troubleshooting, feature docs
├── BCTelemetryDashboard.json   # Main dashboard export
└── README.md
mcp-server/             # MCP server for Claude Code integration
```

## Dashboard pages

| Page | Purpose |
|------|---------|
| **Live Monitoring** | Real-time alerts, error rate, events per minute |
| **Overview** | Key metrics and health summary |
| **Errors & Warnings** | Error trends, top errors by type |
| **Performance: SQL & AL** | Slow queries, slow AL methods, slow pages |
| **Performance: APIs** | Incoming + outgoing web service calls |
| **Performance: Locks** | Deadlocks + lock timeouts |
| **Job Queues** | Job queue health and failures |
| **Extensions** | Usage, unused objects, error rates by extension |
| **Apps** | App lifecycle, installs, updates |
| **Custom Telemetry** | Custom events, tests, BCPT |
| **HAG Web Service** | Hagar web service API monitoring |
| **Daily Maintenance** | Missing indexes, media orphans, retention, features |

## KQL conventions

- Dashboard queries: one query per tile, parameterized with `_startTime`, `_endTime`
- Use `allTraces` as the base table (defined as dashboard parameter)
- Event IDs: Use `customDimensions.eventId` to filter specific BC events (see ExternalData/Signals.json)
- Status indicators: 🔴 Critical, 🟠 Warning, 🟡 Caution, 🟢 OK
- File naming: `<PageName>-<TileName>.kql` for dashboard queries

## Configured Application Insights

| Company | App ID |
|---------|--------|
| Olis | 7fc8b03b-d085-4f31-b68b-7b05f3695f8c |
| Storkaup | 543497be-4606-42cb-8bd3-21ead753bb97 |
| Bananar | 3ac10606-da40-4f12-b216-0d7c2170d33e |

## MCP tools

The `mcp-server/` provides direct telemetry access from Claude Code:
- `list_companies`, `extension_usage`, `error_summary`, `page_usage`
- `unused_objects`, `performance_analysis`, `web_service_usage`
- `job_queue_status`, `custom_query`
