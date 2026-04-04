# BC Telemetry Event ID Quick Reference

Event IDs are in `customDimensions.eventId`. Two naming patterns:
- **RT00xx** — Runtime events (core platform)
- **LC00xx** — Lifecycle events (environment, extensions, companies)
- **AL0000xxx** — Application events (job queues, email, features, etc.)
- **CL00xx** — Client events (page views, user actions)

Full reference: `ExternalData/Signals.json` (269 events)

---

## Most Important Event IDs

### Authentication
| Event ID | Description | Severity |
|----------|-------------|----------|
| RT0001 | Auth Failed (Pre Open Company) | Error |
| RT0002 | Auth Failed (Open Company) | Error |
| RT0003 | Auth Succeeded (Pre Open Company) | Info |
| RT0004 | Auth Succeeded (Open Company) | Info |

### Performance (the ones you see most)
| Event ID | Description | What to look for |
|----------|-------------|------------------|
| **RT0005** | Slow SQL query (exceeded threshold) | `executionTime`, `sqlStatement` in customDimensions |
| **RT0012** | Database lock timed out | Object causing the lock, `alObjectName` |
| **RT0013** | Database lock snapshot | Related to RT0012, contains snapshot details |
| **RT0018** | Slow AL method (exceeded threshold) | `alObjectName`, `alMethodName`, `executionTime` |
| **RT0020** | Web Service Key auth succeeded | Endpoint in customDimensions |
| **RT0021** | Web Service Key auth failed | Endpoint, failure reason |
| **RT0028** | SQL Deadlock | Critical - competing locks killed a process |
| **RT0029** | Session stopped (StopSession) | Session was forcefully terminated |

### Web Services & APIs
| Event ID | Description | What to look for |
|----------|-------------|------------------|
| **RT0008** | Incoming web service call | `endpoint`, `category` (OData/SOAP/API), execution time |
| **RT0019** | Outgoing web service call | `endpoint`, response time, HTTP status |

### Reports
| Event ID | Description |
|----------|-------------|
| RT0006 | Report generated successfully / Report rendering failed |
| RT0007 | Report cancelled |
| RT0011 | Report cancelled but commit occurred (data was changed!) |

### Errors & Dialogs
| Event ID | Description |
|----------|-------------|
| **RT0030** | Error dialog shown to user | 
| **RT0031** | Permission error shown |

### Extension Lifecycle
| Event ID | Description |
|----------|-------------|
| RT0010 | Extension update failed |
| LC0010 | Extension installed successfully |
| LC0011 | Extension install failed |
| LC0012 | Extension uninstalled |
| LC0014 | Extension updated successfully |
| LC0015 | Extension update failed |
| LC0020 | Extension compiled successfully |
| LC0021 | Extension compilation failed |

### Job Queues
| Event ID | Description |
|----------|-------------|
| **AL0000E24** | Job queue entry enqueued |
| **AL0000E25** | Job queue entry started |
| **AL0000E26** | Job queue entry finished |
| AL0000E27 | Job queue entry failed |
| AL0000FNY | Job queue entry NOT enqueued (problem!) |

### Page Views (Client)
| Event ID | Description |
|----------|-------------|
| **CL0001** | Page opened by user |
| CL0002 | User gave error feedback |
| CL0003 | Client action invoked |

### Email
| Event ID | Description |
|----------|-------------|
| AL0000CTV | Email sent successfully |
| AL0000CTP | Email send failed |

### Company & Environment
| Event ID | Description |
|----------|-------------|
| LC0001 | Company created |
| LC0100 | Environment update available |
| LC0105 | Environment update started |
| LC0106 | Environment update completed |

---

## KQL Patterns for Common Scenarios

### Filter by event ID
```kql
traces | where customDimensions.eventId == "RT0005"
```

### Get all errors (any type)
```kql
traces | where severityLevel >= 3
```

### Slow SQL queries
```kql
traces
| where customDimensions.eventId == "RT0005"
| extend 
    ExecutionTime = tolong(customDimensions.executionTime),
    SqlStatement = tostring(customDimensions.sqlStatement),
    Object = tostring(customDimensions.alObjectName)
```

### Job queue failures
```kql
traces
| where customDimensions.eventId in ("AL0000E27", "AL0000FNY")
| extend
    JobId = tostring(customDimensions.alJobQueueId),
    Object = tostring(customDimensions.alObjectName),
    ErrorMessage = tostring(customDimensions.failureReason)
```

### Web service calls with performance
```kql
traces
| where customDimensions.eventId == "RT0008"
| extend
    Endpoint = tostring(customDimensions.endpoint),
    Category = tostring(customDimensions.category),
    ExecutionTime = tolong(customDimensions.serverExecutionTime)
```
