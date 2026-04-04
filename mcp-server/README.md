# BC Telemetry MCP Server

MCP (Model Context Protocol) server sem tengir Claude Code við Azure Application Insights fyrir Olis, Storkaup og Bananar.

## Uppsetning

### 1. Forsendur

```powershell
# Azure CLI þarf að vera uppsett og innskráð
az login
az account set --subscription "YOUR_SUBSCRIPTION_ID"

# Python 3.8+
python --version
```

### 2. Bæta við í Claude Code

```bash
claude mcp add bc-telemetry --transport stdio --scope project -- cmd /c python C:\AL\BCTelemetry\mcp-server\bc_telemetry_mcp.py
```

### 3. Staðfesta uppsetningu

```bash
# Sjá lista af MCP servers
claude mcp list

# Inni í Claude Code
/mcp
```

## Notkun í Claude Code

Þegar MCP server er tengdur geturðu spurt Claude um telemetry gögn:

```
> "Sýndu mér extension notkun hjá Olis síðustu 30 daga"
> "Hvaða villur komu upp hjá Storkaup síðustu 24 tíma?"
> "Finndu ónotaðar síður hjá Bananar"
> "Hvernig er performance á web services hjá Olis?"
```

## Tiltæk tools

| Tool | Lýsing | Parameters |
|------|--------|------------|
| `list_companies` | Sýna fyrirtæki | - |
| `extension_usage` | Extension notkun | company, days |
| `error_summary` | Villur | company, hours |
| `page_usage` | Síðunotkun | company, days |
| `unused_objects` | Ónotuð objects | company, days, threshold |
| `performance_analysis` | Performance | company, days |
| `web_service_usage` | Web service notkun | company, days |
| `job_queue_status` | Job queue staða | company, days |
| `custom_query` | Sérsniðin KQL query | company, query, timespan |

## Application Insights Resources

| Fyrirtæki | App Insights | Resource Group |
|-----------|--------------|----------------|
| Olis | Olis-Application-Insights | rg-BC_Teymi |
| Storkaup | Storkaup-Application-Insights | rg-BC_Teymi |
| Bananar | Bananar-Application-Insights | rg-BC_Teymi |

## Dæmi um sérsniðna query

```
> "Keyrðu þessa KQL query á Olis: traces | where timestamp > ago(1h) | count"
```

Claude mun nota `custom_query` tool til að keyra queryið.

## Villuleit

### "az: command not found"
Azure CLI er ekki uppsett eða ekki í PATH.

```powershell
winget install Microsoft.AzureCLI
# Endurræsa terminal
```

### "Please run 'az login'"
Þú þarft að skrá þig inn í Azure.

```powershell
az login
```

### "ResourceNotFound"
App Insights nafn eða resource group er rangt. Athugaðu stillingar í `bc_telemetry_mcp.py`.
