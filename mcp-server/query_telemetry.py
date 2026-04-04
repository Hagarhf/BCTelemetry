#!/usr/bin/env python3
"""
BC Telemetry Query Tool
=======================
Keyrir KQL queries á Azure Application Insights.

Notkun:
    python query_telemetry.py <company> <tool> [params...]

Dæmi:
    python query_telemetry.py olis errors 24
    python query_telemetry.py storkaup usage 30
    python query_telemetry.py bananar pages 7
"""

import json
import subprocess
import sys

# Application Insights configurations
APP_INSIGHTS = {
    "olis": {
        "name": "Olis-Application-Insights",
        "resource_group": "rg-BC_Teymi"
    },
    "storkaup": {
        "name": "Storkaup-Application-Insights",
        "resource_group": "rg-BC_Teymi"
    },
    "bananar": {
        "name": "Bananar-Application-Insights-Resource",
        "resource_group": "rg-BC_Teymi"
    }
}

def run_query(query: str, company: str, timespan: str = "P7D") -> dict:
    """Keyra KQL query."""
    config = APP_INSIGHTS.get(company.lower(), APP_INSIGHTS["olis"])

    # Build the az command as a string for shell execution
    cmd = f'az monitor app-insights query --app "{config["name"]}" --resource-group "{config["resource_group"]}" --analytics-query "{query}" --timespan "{timespan}" --output json'

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, shell=True)

    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        return {"error": result.stderr}

def get_errors(company: str, hours: int = 24):
    """Sýna villur."""
    query = f"""
traces
| where timestamp > ago({hours}h)
| where severityLevel >= 3
| extend extensionName = tostring(customDimensions.extensionName)
| summarize ErrorCount = count(), SampleError = any(message) by extensionName
| order by ErrorCount desc
| take 20
"""
    return run_query(query, company, f"PT{hours}H")

def get_usage(company: str, days: int = 30):
    """Sýna extension notkun."""
    query = f"""
traces
| where timestamp > ago({days}d)
| extend extensionName = tostring(customDimensions.extensionName)
| where isnotempty(extensionName)
| summarize ActivityCount = count(), UniqueUsers = dcount(user_Id) by extensionName
| order by ActivityCount desc
| take 30
"""
    return run_query(query, company, f"P{days}D")

def get_pages(company: str, days: int = 30):
    """Sýna síðunotkun."""
    query = f"""
traces
| where timestamp > ago({days}d)
| extend eventId = tostring(customDimensions.eventId)
| where eventId == "RT0005"
| extend pageName = tostring(customDimensions.alObjectName)
| extend extensionName = tostring(customDimensions.extensionName)
| where isnotempty(pageName)
| summarize OpenCount = count() by pageName, extensionName
| order by OpenCount desc
| take 30
"""
    return run_query(query, company, f"P{days}D")

def get_performance(company: str, days: int = 7):
    """Sýna performance."""
    query = f"""
traces
| where timestamp > ago({days}d)
| extend objectName = tostring(customDimensions.alObjectName)
| extend extensionName = tostring(customDimensions.extensionName)
| extend ms = todouble(customDimensions.serverExecutionTime)
| where isnotempty(objectName) and ms > 0
| summarize P95 = round(percentile(ms, 95), 0) by objectName, extensionName
| where P95 > 500
| order by P95 desc
| take 20
"""
    return run_query(query, company, f"P{days}D")

def custom_query(company: str, kql: str, timespan: str = "P7D"):
    """Keyra sérsniðna query."""
    return run_query(kql, company, timespan)

def main():
    if len(sys.argv) < 3:
        print("Notkun: python query_telemetry.py <company> <tool> [params...]")
        print("Companies: olis, storkaup, bananar")
        print("Tools: errors, usage, pages, performance, query")
        sys.exit(1)

    company = sys.argv[1]
    tool = sys.argv[2]

    if company.lower() not in APP_INSIGHTS:
        print(f"Villa: Óþekkt fyrirtæki '{company}'. Notaðu: olis, storkaup, bananar")
        sys.exit(1)

    result = None

    if tool == "errors":
        hours = int(sys.argv[3]) if len(sys.argv) > 3 else 24
        result = get_errors(company, hours)
    elif tool == "usage":
        days = int(sys.argv[3]) if len(sys.argv) > 3 else 30
        result = get_usage(company, days)
    elif tool == "pages":
        days = int(sys.argv[3]) if len(sys.argv) > 3 else 30
        result = get_pages(company, days)
    elif tool == "performance":
        days = int(sys.argv[3]) if len(sys.argv) > 3 else 7
        result = get_performance(company, days)
    elif tool == "query":
        if len(sys.argv) < 4:
            print("Villa: KQL query vantar")
            sys.exit(1)
        kql = sys.argv[3]
        timespan = sys.argv[4] if len(sys.argv) > 4 else "P7D"
        result = custom_query(company, kql, timespan)
    else:
        print(f"Villa: Óþekkt tool '{tool}'. Notaðu: errors, usage, pages, performance, query")
        sys.exit(1)

    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
