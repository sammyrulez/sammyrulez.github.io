---
title: "Dirigista: Stop Asking Your Agent to Judge, Start Asking It to Delegate"
date: 2026-10-11 10:00
tags:
- AI
- LLM
- MCP
- typesafe
- agents
category: blog
author: samreghenzi
description: "An MCP server that turns \"is this urgent?\", \"which team owns this?\" and \"is this true?\" into calibrated probabilities instead of eloquent guesses."
slug: dirigista-letting-agents-delegate-judgment
---

Every agent I have built ends up doing the same thing, sooner or later: making small judgments about text. Is this support ticket about billing or about a bug? How angry is this customer? Does this paragraph actually answer the question? Is this claim true according to the document I was given?

We usually let the big model handle these inline. It is right there, it is smart, it costs nothing extra to ask. And it answers — always, fluently, with total confidence. That last part is the problem.

A large language model asked to classify something will give you a label. It will not tell you whether that label was a 95% call or a coin flip, because it doesn't really know. If you ask for a confidence, it will write a number, and that number is prose shaped like a probability. If you ask for an explanation, it will produce one — after the fact, rationalising a decision that was never made by reasoning in the first place.

`dirigista` is my attempt to take those judgments away from the generalist and hand them to something built for them.

## What it is

`dirigista` is a small [MCP](https://modelcontextprotocol.io) server that exposes three classification tools to any MCP client — Claude Code, Claude Desktop, Cursor, whatever speaks the protocol. Behind the tools sits a specialised inference backend that does not generate text at all: it returns typed judgments with calibrated probabilities.

The name is Italian: a *dirigista* is someone who directs — the economy, traffic, an orchestra. The agent stays the conductor; it just stops playing every instrument itself.

The server's own instructions to the calling model say it bluntly:

> Delegate any classification of text to these tools instead of judging it yourself: routing, triage, labelling, moderation, prioritising, sentiment, intent, relevance and fact checks. One item per call.

## Three tools, three shapes of question

Almost every classification task I have met in real systems collapses into one of three questions. `dirigista` has exactly one tool for each.

### `verify` — is it true?

You give it a statement and, optionally, a context to judge it against. You get back a single probability and a verdict derived from it.

```json
{ "verdict": "uncertain", "probability": 0.51 }
```

The verdict is **three-valued on purpose**: `true`, `false`, or `uncertain`. The probability is read against two thresholds, `false_below` (default 0.2) and `true_above` (default 0.8), and anything in between is honestly reported as undecided.

My favourite example: ask whether *"Water is wet"*. The model returns about 0.51. Water makes other things wet, but whether water itself *is* wet is a genuine dispute — and the tool says so instead of picking a side to look decisive.

The thresholds are yours to move. If a false positive costs you far more than a false negative — say, auto-closing tickets flagged as "resolved" — push `true_above` to 0.95 and let more cases fall into `uncertain`, where a human looks at them. The defaults are a convention, not a fact about your domain.

### `categorize` — which one is it?

You give it a statement and a list of categories. You get the winner, its confidence, and the full distribution (numbers below are illustrative):

```json
{
  "category": "Billing",
  "confidence": 0.87,
  "probabilities": { "Billing": 0.87, "Bug report": 0.09, "Feature request": 0.04 }
}
```

There is no built-in taxonomy: the categories are part of every request, so the same server routes support tickets in the morning and labels pull requests in the afternoon. The full distribution matters more than it looks. A flat spread tells you your categories were not well separated *for this input* — which is exactly the signal you want before routing something automatically.

One practical rule: the model cannot pick an option you did not offer. If your list might not cover every input, add a `"none of the above"`.

### `score` — how much?

You give it a statement and a list of criteria, ordered from lowest to highest. It returns the level that best fits, its 1-based position on the scale, and a confidence.

```json
{
  "statement": "I have asked for a refund three times and nobody has replied.",
  "criteria": [
    "Calm, just stating facts",
    "Frustrated but civil",
    "Very angry, strong language"
  ]
}
```

→ illustratively, `{ "criterion": "Frustrated but civil", "level": 2, "confidence": 0.8 }`

Two details here are worth calling out, because they are design decisions rather than accidents.

First, **describe your levels in words**. `["low", "medium", "high"]` gives the model almost nothing to anchor on; `"Frustrated but civil"` does. Concrete descriptions rate far more reliably.

Second, the backend's raw score is a probability-weighted mean, which can land between levels — 1.43 on a three-point scale. The naïve move is to round it. But rounding a mean answers a different question ("what is the average intensity?") from the one the caller asked ("which level is this?"). So `score` returns the **most probable** level instead. On a bimodal distribution the two answers can diverge, and only one of them is a level the statement actually sits at.

## No rationale, by design

None of the three tools returns an explanation. No `reasoning` field, no "because…".

This is the decision people push back on most, and the one I am most sure about. The backend produces probabilities, not prose. Any explanation attached to its output would have to be generated *afterwards*, by something else, to justify a number it did not produce. That is not an explanation; it is a story. And an invented rationale is worse than none, because it looks like evidence.

Trust in `dirigista` is carried by the numbers. A 0.97 and a 0.52 are different answers, and the caller — human or agent — can act on that difference: automate the first, escalate the second.

<figure class="diagram">
  <a href="/images/dirigista-decisions.png" title="Click to enlarge"><img src="/images/dirigista-decisions.png" alt="Before: the agent judges inline and acts on a label with prose confidence. After: the agent calls dirigista over MCP, Jev returns a calibrated probability, and thresholds in code decide whether to automate, escalate to a human or reject."></a>
  <figcaption>Same question, two pipelines: a label with prose confidence versus a calibrated probability routed by thresholds in code.</figcaption>
</figure>

## Why bother, when the big model can just answer?

A few reasons, in increasing order of importance.

**Cost and latency.** A specialised classifier is cheaper and faster than spending a frontier model's tokens on "billing or bug?". The tool definitions themselves are kept under a strict budget — under 1,000 tokens for all three tools plus the server instructions — because MCP re-sends them on every request. Context is not free, and a tool you install everywhere should behave like it knows that.

**Separation of concerns.** The agent plans, converses and acts; the classifier judges. When a routing decision goes wrong, you know which component made it, and you can test it in isolation.

**Calibration.** This is the real one. A calibrated 0.8 means that, across many such answers, about 80% are right. That is what lets you put a threshold in code and sleep at night. A generative model's "I'm fairly confident" doesn't give you that guarantee, no matter how politely you prompt it.

**Composability.** Probabilities combine. You can chain a `categorize` into a `score`, gate an action on `verify(...).probability > 0.9`, or log the distributions and see drift over time. Prose doesn't compose; numbers do.

## How it is built

The architecture is deliberately boring, with one direction of dependency:

```
server.py  → classifiers.py → client.py
(MCP only)   (logic only)     (credentials only)
             models.py (contracts, shared)
telemetry.py (spans; used by server.py only)
```

- `server.py` registers the tools and holds no logic: validate, open a client, delegate, serialise. Its docstrings are product surface — they are what the calling model reads to decide when to use each tool — so they are written and measured like UI copy.
- `classifiers.py` knows nothing about MCP. It builds the question for the backend and converts the typed answer into a Pydantic result. The client is injected as a parameter, so the whole conversion logic is tested against a fake client that records requests and replays canned answers — no network, no cost.
- `client.py` resolves credentials and nothing else.

On top of that sits an opt-in live test suite that talks to the real API through a real MCP client session, because some bugs only exist at the boundary.

### Two lessons from the boundary

**MCP clients strip the environment.** The server runs as a subprocess with only `HOME`, `LOGNAME`, `PATH`, `SHELL`, `TERM` and `USER`. An API key exported in your shell never arrives. So `dirigista` falls back to a `.env` file in the working directory — but only that directory, never parent directories.

**The environment is trusted; a `.env` file is not.** It would have been easy to call `load_dotenv()` and move on. But loading a file means every line in it takes effect on the process, and both the SDK and the HTTP stack resolve things like base URLs, proxies and certificate bundles from the environment. One planted line in a `.env` would redirect your API key — and every statement you classify — to someone else's host. So the server *reads* the key out of the file and ignores everything else.

### Telemetry that doesn't leak

Tracing is OpenTelemetry, off by default, switched on only when `OTEL_EXPORTER_OTLP_ENDPOINT` is set in the real environment (a `.env` can't turn it on, for the same reason as above). Each tool call becomes a span carrying **metadata only**: statement length, number of categories, the verdict, the level, the confidence, the error type.

Never the statement, the context, the categories, the criteria — and not even exception messages, which have a habit of quoting the input back. If you classify customer emails, your tracing backend learns how long they were and how confident the classifier felt. Nothing more. A dedicated test guards that rule, so a future attribute can't quietly break it.

## Trying it

Classification runs on [TypeSafe](https://docs.typesafe.ai)'s Jev model (the same one I [benchmarked against a GPT agent loop](/typesafe-jev-vs-agentic-loop.html) last month), so you need an API key from [console.typesafe.ai](https://console.typesafe.ai/). Then, in Claude Code, one command:

```sh
claude mcp add dirigista -e TYPESAFE_API_KEY=your-key -- \
  uvx --from git+https://github.com/sammyrulez/dirigista dirigista
```

For Claude Desktop there is a `dirigista.mcpb` bundle in the [latest release](https://github.com/sammyrulez/dirigista/releases/latest): open it, paste the key into the dialog, done. Any other MCP client takes the usual `mcpServers` JSON snippet from the README.

## The broader point

We have spent two years making language models better at *saying* things. A lot of what our systems actually need from them is not saying — it is deciding, small and often, with a known error rate. Those decisions deserve a component that answers in the currency of decisions: probabilities, thresholds, distributions.

`dirigista` is a small step in that direction. Let the agent conduct. Let something calibrated keep time.
