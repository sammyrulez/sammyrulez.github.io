---
title: "Giving voice to Italian energy markets with artificial intelligence"
date: 2026-04-12 22:48
tags:
- AI
- LLM
- MCP
- Python
category: blog
author: samreghenzi
description:  "How an MCP server turns electricity exchange data into natural conversations"
---





## How an MCP server turns electricity exchange data into natural conversations

The Italian electricity market produces an enormous amount of data every day: hourly prices by zone, traded volumes, liquidity, the PUN (Prezzo Unico Nazionale — the national single price). Essential data for traders, energy analysts, industry journalists, and companies operating in the energy sector. Yet accessing this data still means navigating web portals, downloading CSVs, and writing ad-hoc scripts. A fragmented and slow workflow.

With **mercati-energetici-mcp** I set out to change the approach: making GME (Gestore dei Mercati Energetici — the Italian Energy Markets Operator) data directly accessible from within the AI assistants we already use every day — Claude, Copilot, and any other tool compatible with the MCP protocol.

## What is MCP and why it changes the game

The **Model Context Protocol** is an open standard that allows language models to interact with external services in a structured way. Think of it as a bridge: on one side there's the AI that knows how to reason, on the other there's real-world data. MCP connects them.

Before MCP, getting an LLM to access market data required building custom integrations, prompt engineering pipelines, or manually copying and pasting data into the conversation context. With MCP, you simply declare **tools** — functions the AI can invoke autonomously whenever it needs them.

The difference is substantial: you no longer have to retrieve the data yourself and then ask the AI to analyze it. The AI itself, during the conversation, decides when and which data it needs and retrieves it on its own.

## The implementation: Python, FastMCP, and simplicity

The project is intentionally minimal. A single Python file, about 150 lines of code, exposing 5 tools:

- **get_prices** — hourly energy prices by zone and day
- **get_volumes** — bought and sold volumes on the market
- **get_liquidity** — hourly market liquidity percentage
- **daily_pun** — daily national average price
- **get_zones** — list of available market zones

The [mercati-energetici](https://github.com/sammyrulez/mercati-energetici) library handles the interaction with the official GME APIs. [FastMCP](https://github.com/jlowin/fastmcp) manages the entire MCP protocol, turning simple Python functions decorated with `@server.tool()` into endpoints that any MCP client can discover and invoke.

The code for a tool is disarmingly simple:

```python
@server.tool()
async def get_prices(day: Optional[str] = None, zone: str = "PUN") -> str:
    """Get electricity prices in €/MWh for a specific day and zone."""
    async with init_MGP() as mgp:
        result = await mgp.get_prices(day=day, zone=zone)
        return json.dumps({"prices": result, "unit": "€/MWh", "zone": zone})
```

No boilerplate, no complex configuration. The docstring automatically becomes the description the AI reads to understand when and how to use the tool. The type hints on parameters become the JSON schema that the protocol uses for validation.

## Integration with Claude and Copilot

### Claude Desktop and Claude Code

Once the server is configured in Claude's config, electricity market data becomes a natural part of the conversation. You can ask:

> "What was the price of energy in Sicily yesterday?"

Claude doesn't search the internet, doesn't hallucinate a number: it invokes `get_prices` with the correct parameters and returns the actual data from GME. You can go further:

> "Compare today's prices between Northern and Southern Italy and tell me if there's a significant gradient"

The AI calls the tool twice, once per zone, and then reasons on the real data to produce an analysis.

> "Show me the PUN trend over the last week and identify any anomalies"

Here Claude chains multiple calls to `daily_pun` for different days, builds a time series, and applies its analytical reasoning on concrete data.

### GitHub Copilot

With MCP support expanding across the Copilot ecosystem as well, the same server can power energy analyses directly within the IDE. A data analyst writing Python code for a report can have market data at prompt's reach, without leaving VS Code.

### Any MCP client

The beauty of an open standard is that you're not locked into a vendor. Any tool that speaks MCP — present or future — can connect to this server and access Italian electricity market data.

## Concrete use cases

**For the energy trader**: quick analysis of zonal prices, cross-zone comparison, pattern identification in traded volumes. All in natural language, without having to open spreadsheets.

**For the industry analyst**: automatic generation of daily or weekly reports on the electricity market, with AI-produced commentary and interpretations based on real data.

**For the journalist**: immediate access to market data for articles and in-depth pieces, with the ability to ask the AI for explanations and context.

**For the developer**: a concrete example of how to build an MCP server for a vertical domain, reusable as a template for other markets or data sources.

**For the energy company**: integration of exchange data into internal workflows, from customer service answering pricing questions to the procurement office monitoring the market.

## The value of the MCP approach

The real innovation isn't in the code — it's in the paradigm. We're moving from a model where the user is the intermediary between data and AI, to one where the AI accesses data directly and uses it within the conversation context.

This means:

- **No more copy-paste**: data flows directly into the AI's reasoning
- **Always up-to-date data**: every request queries the GME APIs in real time
- **Contextual analysis**: the AI can combine data from multiple calls to produce insights that would otherwise require manual work
- **Accessibility**: anyone can query the electricity market in natural language, without specific technical skills

## Getting started

The project is open source under the MIT license. To try it you need:

1. Python 3.12+ and [uv](https://github.com/astral-sh/uv) as a package manager
2. A GME account with API access (request it at [mercatoelettrico.org](https://www.mercatoelettrico.org/))
3. An MCP client — Claude Desktop, Claude Code, or any other compatible one

```bash
git clone https://github.com/sammyrulez/mercati-energetici-mcp
cd mercati-energetici-mcp
uv sync
```

Configure your credentials and you're up and running. Less than 5 minutes from installation to your first natural language query about energy prices.

## Conclusion

The Italian electricity market is a data-rich domain but historically not very accessible. With an MCP server of just a few lines of code, this data becomes an integral part of AI conversations — transforming a fragmented workflow into a fluid and natural dialogue.

It's a small project, but it represents a powerful pattern: any structured data source can become an MCP tool, and therefore become accessible through natural language. Energy markets are just the beginning.
