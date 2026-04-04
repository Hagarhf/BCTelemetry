#!/usr/bin/env python3
"""
BC Telemetry MCP Server
=======================
MCP server fyrir Claude Code sem tengist Azure Application Insights
og keyrir KQL queries fyrir Olis, Storkaup og Bananar.

Notkun:
    claude mcp add bc-telemetry --transport stdio -- cmd /c python C:\AL\BCTelemetry\mcp-server\bc_telemetry_mcp.py
"""

import json
import subprocess
import sys
import os
from pathlib import Path
from typing import Optional

# Application Insights configurations
APP_INSIGHTS = {
    "olis": {
        "name": "Olis-Application-Insights",
        "resource_group": "rg-BC_Teymi",
        "app_id": "7fc8b03b-d085-4f31-b68b-7b05f3695f8c"
    },
    "storkaup": {
        "name": "Storkaup-Application-Insights",
        "resource_group": "rg-BC_Teymi",
        "app_id": "543497be-4606-42cb-8bd3-21ead753bb97"
    },
    "bananar": {
        "name": "Bananar-Application-Insights-Resource",
        "resource_group": "rg-BC_Teymi",
        "app_id": "3ac10606-da40-4f12-b216-0d7c2170d33e"
    }
}

# KQL queries directory
KQL_DIR = Path(r"C:\AL\BCTelemetry\Azure Data Explorer")


def run_az_query(query: str, app_insights: str, resource_group: str, timespan: str = "P30D") -> dict:
    """Keyra KQL query gegnum Azure CLI."""
    try:
        # Escape quotes in query for command line
        escaped_query = query.replace('"', '\\"')

        cmd = [
            "az", "monitor", "app-insights", "query",
            "--app", app_insights,
            "--resource-group", resource_group,
            "--analytics-query", query,
            "--timespan", timespan,
            "--output", "json"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )

        if result.returncode == 0:
            return {"success": True, "data": json.loads(result.stdout)}
        else:
            return {"success": False, "error": result.stderr}

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Query timeout (>2 minutes)"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_app_config(company: str) -> dict:
    """Sækja App Insights config fyrir fyrirtæki."""
    company_lower = company.lower()
    if company_lower in APP_INSIGHTS:
        return APP_INSIGHTS[company_lower]
    return APP_INSIGHTS["olis"]  # Default to Olis


# ============================================================================
# BC Telemetry Queries
# ============================================================================

def extension_usage(company: str = "olis", days: int = 30) -> dict:
    """
    Sýna notkun extensions síðustu N daga.
    Skilar: extensionName, ActivityCount, UniqueUsers, UsageLevel
    """
    config = get_app_config(company)
    query = f"""
    traces
    | where timestamp > ago({days}d)
    | extend extensionName = tostring(customDimensions.extensionName)
    | extend extensionPublisher = tostring(customDimensions.extensionPublisher)
    | where isnotempty(extensionName)
    | summarize
        ActivityCount = count(),
        UniqueUsers = dcount(user_Id),
        LastActivity = max(timestamp)
        by extensionName, extensionPublisher
    | extend UsageLevel = case(
        ActivityCount < 10, "Low",
        ActivityCount < 100, "Moderate",
        ActivityCount < 1000, "Active",
        "Heavy"
    )
    | order by ActivityCount desc
    | take 50
    """
    return run_az_query(query, config["name"], config["resource_group"], f"P{days}D")


def error_summary(company: str = "olis", hours: int = 24) -> dict:
    """
    Sýna villur síðustu N klukkustundir.
    Skilar: extensionName, ErrorCount, SampleError
    """
    config = get_app_config(company)
    query = f"""
    traces
    | where timestamp > ago({hours}h)
    | where severityLevel >= 3
    | extend extensionName = tostring(customDimensions.extensionName)
    | summarize
        ErrorCount = count(),
        UniqueErrors = dcount(message),
        LastError = max(timestamp),
        SampleError = any(message)
        by extensionName
    | order by ErrorCount desc
    | take 20
    """
    return run_az_query(query, config["name"], config["resource_group"], f"PT{hours}H")


def page_usage(company: str = "olis", days: int = 30) -> dict:
    """
    Sýna notkun síðna (pages) síðustu N daga.
    Skilar: pageName, OpenCount, UniqueUsers
    """
    config = get_app_config(company)
    query = f"""
    traces
    | where timestamp > ago({days}d)
    | extend eventId = tostring(customDimensions.eventId)
    | where eventId == "RT0005"
    | extend pageName = tostring(customDimensions.alObjectName)
    | extend pageId = tostring(customDimensions.alObjectId)
    | extend extensionName = tostring(customDimensions.extensionName)
    | where isnotempty(pageName)
    | summarize
        OpenCount = count(),
        UniqueUsers = dcount(user_Id),
        LastOpened = max(timestamp)
        by pageName, pageId, extensionName
    | order by OpenCount desc
    | take 50
    """
    return run_az_query(query, config["name"], config["resource_group"], f"P{days}D")


def unused_objects(company: str = "olis", days: int = 30, threshold: int = 5) -> dict:
    """
    Finna objects með litla eða enga notkun.
    Skilar: objectName, objectType, UsageCount, RecommendedAction
    """
    config = get_app_config(company)

    # Determine publisher filter based on company
    publishers = {
        "olis": '"Olis", "OC"',
        "storkaup": '"Storkaup", "NVL", "Hagar"',
        "bananar": '"eRey", "Bananar"'
    }
    publisher_filter = publishers.get(company.lower(), '"Olis"')

    query = f"""
    traces
    | where timestamp > ago({days}d)
    | extend
        extensionName = tostring(customDimensions.extensionName),
        extensionPublisher = tostring(customDimensions.extensionPublisher),
        alObjectType = tostring(customDimensions.alObjectType),
        alObjectId = tostring(customDimensions.alObjectId),
        alObjectName = tostring(customDimensions.alObjectName)
    | where extensionPublisher in ({publisher_filter})
    | where isnotempty(alObjectId) and alObjectId != "-1"
    | summarize
        UsageCount = count(),
        LastSeen = max(timestamp)
        by extensionName, alObjectType, alObjectId, alObjectName
    | where UsageCount < {threshold}
    | extend RecommendedAction = case(
        UsageCount == 0, "Consider removing",
        UsageCount < 3, "Review - Very rare usage",
        "Monitor"
    )
    | order by UsageCount asc
    | take 50
    """
    return run_az_query(query, config["name"], config["resource_group"], f"P{days}D")


def performance_analysis(company: str = "olis", days: int = 7) -> dict:
    """
    Greina performance - hægir síður og codeunits.
    Skilar: objectName, P95ExecutionTimeMs, PerformanceRating
    """
    config = get_app_config(company)
    query = f"""
    traces
    | where timestamp > ago({days}d)
    | extend extensionName = tostring(customDimensions.extensionName)
    | extend objectName = tostring(customDimensions.alObjectName)
    | extend executionTimeMs = todouble(customDimensions.serverExecutionTime)
    | where isnotempty(objectName) and executionTimeMs > 0
    | summarize
        TotalExecutions = count(),
        AvgExecutionTimeMs = round(avg(executionTimeMs), 2),
        P95ExecutionTimeMs = round(percentile(executionTimeMs, 95), 2),
        MaxExecutionTimeMs = round(max(executionTimeMs), 2)
        by extensionName, objectName
    | extend PerformanceRating = case(
        P95ExecutionTimeMs < 100, "Excellent",
        P95ExecutionTimeMs < 500, "Good",
        P95ExecutionTimeMs < 2000, "Acceptable",
        "Slow"
    )
    | where P95ExecutionTimeMs > 500
    | order by P95ExecutionTimeMs desc
    | take 30
    """
    return run_az_query(query, config["name"], config["resource_group"], f"P{days}D")


def web_service_usage(company: str = "olis", days: int = 30) -> dict:
    """
    Sýna notkun web services og API endpoints.
    Skilar: endpoint, CallCount, SuccessRate, AvgExecutionTimeMs
    """
    config = get_app_config(company)
    query = f"""
    traces
    | where timestamp > ago({days}d)
    | extend eventId = tostring(customDimensions.eventId)
    | where eventId in ("RT0008", "RT0030")
    | extend endpoint = tostring(customDimensions.endpoint)
    | extend extensionName = tostring(customDimensions.extensionName)
    | extend httpStatusCode = tostring(customDimensions.httpStatusCode)
    | extend executionTimeMs = todouble(customDimensions.serverExecutionTime)
    | summarize
        CallCount = count(),
        SuccessCount = countif(httpStatusCode startswith "2"),
        ErrorCount = countif(httpStatusCode startswith "4" or httpStatusCode startswith "5"),
        AvgExecutionTimeMs = round(avg(executionTimeMs), 2)
        by endpoint, extensionName
    | extend SuccessRate = round(todouble(SuccessCount) / todouble(CallCount) * 100, 2)
    | order by CallCount desc
    | take 30
    """
    return run_az_query(query, config["name"], config["resource_group"], f"P{days}D")


def job_queue_status(company: str = "olis", days: int = 7) -> dict:
    """
    Sýna stöðu job queue entries.
    Skilar: codeunitName, ExecutionCount, SuccessCount, ErrorCount
    """
    config = get_app_config(company)
    query = f"""
    traces
    | where timestamp > ago({days}d)
    | extend eventId = tostring(customDimensions.eventId)
    | where eventId == "RT0012"
    | extend codeunitName = tostring(customDimensions.alObjectName)
    | extend extensionName = tostring(customDimensions.extensionName)
    | extend jobStatus = tostring(customDimensions.result)
    | summarize
        ExecutionCount = count(),
        SuccessCount = countif(jobStatus == "Success"),
        ErrorCount = countif(jobStatus in ("Error", "Failed")),
        LastRun = max(timestamp)
        by codeunitName, extensionName
    | extend SuccessRate = round(todouble(SuccessCount) / todouble(ExecutionCount) * 100, 2)
    | order by ExecutionCount desc
    | take 30
    """
    return run_az_query(query, config["name"], config["resource_group"], f"P{days}D")


def custom_query(company: str, query: str, timespan: str = "P7D") -> dict:
    """
    Keyra sérsniðna KQL query.
    """
    config = get_app_config(company)
    return run_az_query(query, config["name"], config["resource_group"], timespan)


def list_companies() -> dict:
    """Sýna lista af fyrirtækjum/App Insights resources."""
    return {
        "success": True,
        "data": {
            "companies": list(APP_INSIGHTS.keys()),
            "details": APP_INSIGHTS
        }
    }


# ============================================================================
# MCP Protocol Handler
# ============================================================================

TOOLS = {
    "list_companies": {
        "func": list_companies,
        "description": "Sýna lista af fyrirtækjum (Olis, Storkaup, Bananar)"
    },
    "extension_usage": {
        "func": extension_usage,
        "description": "Sýna notkun extensions",
        "params": ["company", "days"]
    },
    "error_summary": {
        "func": error_summary,
        "description": "Sýna villur síðustu klukkustundir",
        "params": ["company", "hours"]
    },
    "page_usage": {
        "func": page_usage,
        "description": "Sýna notkun síðna (pages)",
        "params": ["company", "days"]
    },
    "unused_objects": {
        "func": unused_objects,
        "description": "Finna objects með litla notkun",
        "params": ["company", "days", "threshold"]
    },
    "performance_analysis": {
        "func": performance_analysis,
        "description": "Greina performance - hægir síður og codeunits",
        "params": ["company", "days"]
    },
    "web_service_usage": {
        "func": web_service_usage,
        "description": "Sýna notkun web services og API",
        "params": ["company", "days"]
    },
    "job_queue_status": {
        "func": job_queue_status,
        "description": "Sýna stöðu job queue entries",
        "params": ["company", "days"]
    },
    "custom_query": {
        "func": custom_query,
        "description": "Keyra sérsniðna KQL query",
        "params": ["company", "query", "timespan"]
    }
}


def handle_request(request: dict) -> dict:
    """Handle MCP tool request."""
    tool_name = request.get("tool", "")
    params = request.get("params", {})

    if tool_name == "list_tools":
        return {
            "success": True,
            "data": {
                name: {"description": info["description"], "params": info.get("params", [])}
                for name, info in TOOLS.items()
            }
        }

    if tool_name in TOOLS:
        try:
            return TOOLS[tool_name]["func"](**params)
        except TypeError as e:
            return {"success": False, "error": f"Invalid parameters: {e}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    return {"success": False, "error": f"Unknown tool: {tool_name}"}


def main():
    """Main MCP server loop - reads from stdin, writes to stdout."""
    # Log startup to stderr (not stdout which is for MCP protocol)
    print("BC Telemetry MCP Server started", file=sys.stderr)
    print(f"Available tools: {list(TOOLS.keys())}", file=sys.stderr)

    for line in sys.stdin:
        try:
            line = line.strip()
            if not line:
                continue

            request = json.loads(line)
            response = handle_request(request)

            # Output response as JSON
            print(json.dumps(response, ensure_ascii=False))
            sys.stdout.flush()

        except json.JSONDecodeError as e:
            error_response = {"success": False, "error": f"Invalid JSON: {e}"}
            print(json.dumps(error_response))
            sys.stdout.flush()
        except Exception as e:
            error_response = {"success": False, "error": str(e)}
            print(json.dumps(error_response))
            sys.stdout.flush()


if __name__ == "__main__":
    main()
