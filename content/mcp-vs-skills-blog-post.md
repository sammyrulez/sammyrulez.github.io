---
title: "MCP vs Skills: when to use which in professional LLM-assisted coding"
date: 2026-05-10 22:48
tags:
- AI
- LLM
- MCP
- Python
category: blog
author: samreghenzi
description:  "A practical guide for teams integrating language models into their development workflows without burning tokens (and budget)"
---


Anyone who has spent years doing systems integration immediately understands the appeal of MCP. The dream in this field has always been the same: a clean contract between systems, where every method is described, every parameter is typed, every response is predictable. No more 80-page PDFs read half-heartedly, no more reverse engineering undocumented APIs, no more "ask Dave, he knows how it works." Just a schema, and everything else follows.

MCP delivers exactly that dream — but for language models. An MCP server exposes its tools with human-readable descriptions, structured parameters, defined types. The model reads the schema and *already knows what it can do and how to do it*. For anyone coming from systems integration, it's almost moving: it feels like someone finally applied the principles of good API design to the problem of making LLMs collaborate with the outside world.

The appeal is undeniable. And justified — MCP is genuinely a good idea, well executed.

But it's not a silver bullet. Like almost every elegant solution in software architecture, it comes with trade-offs that only become visible when you start using it in production, on real problems, with real constraints of cost and latency.

---

## The problem nobody tells you about

When a team starts using LLMs seriously for coding, they inevitably reach a fork in the road: how do you make the model interact with the outside world? How do you give it access to the right tools without turning every request into an exercise in token waste?

Two dominant approaches exist: **MCP servers** (Model Context Protocol) and **CLI-based skills**. They are not equivalent. Choosing the wrong one has a real cost — in latency, inference costs, and maintenance complexity.

---

## What they are, briefly

**MCP** is a standardized protocol that allows the model to interact with external services through a structured interface. The MCP server exposes tools, resources, and prompts that the model can invoke natively, with authentication and state managed server-side.

**CLI-based skills** are a more hands-on approach: you teach the model to use command-line tools by documenting how to invoke them, which flags they accept, what they return. The model learns to progressively "discover" the tool's capabilities, much like a developer consulting a man page for the first time.

---

## When MCP is the right choice

MCP shines in one specific case: when you need to integrate **complex external systems that don't naturally speak the language of text**.

Think Canva. Or Figma. Or a BI system that generates interactive charts, a DAW for audio production, a 3D rendering platform. These systems have rich APIs, complex state management, OAuth authentication, webhooks, binary assets. They are not designed to be consumed or produced as text — they are designed to be *used*, with clicks, drags, graphical parameters, visual previews.

In these cases, an MCP server does excellent work:

- **Abstracts complexity**: the model doesn't need to know how Canva's API works internally. It only knows that a `create_presentation` tool exists with certain parameters.
- **Manages state**: authentication, session tokens, user context — everything lives in the MCP server, not in the prompt.
- **Is type-safe**: MCP tools have defined schemas. The model receives structured feedback, not raw text to parse.
- **Is auditable**: every tool call is loggable, traceable, revocable.

A concrete example: you want the model to automatically generate documentation slides from your code. With MCP you can integrate Canva or Google Slides directly, with access to company templates, brand fonts, layout systems — things that via CLI would be impossible or would require a massive wrapper.

---

## When CLI Skills are superior

For **everyday professional coding**, CLI-based skills beat MCP on one fundamental point: **token usage**.

Consider what happens when you use an MCP server: at context initialization, the model must receive the full list of available tools, with their schemas, descriptions, and parameters. If the server exposes 40 tools (perfectly normal for an enterprise integration), you're burning hundreds or thousands of tokens *before making a single useful request*.

CLI skills work differently. They work the way an experienced developer works: in a **progressive and contextual** manner.

The model learns that a tool exists (say `gh` for GitHub CLI, or `kubectl`, or `terraform`). When it needs to do something, it can invoke `gh --help` or `gh issue --help` to discover exactly the flags it needs, *at the moment it needs them*. It doesn't hold everything in its head from the start — it discovers progressively.

This leads to concrete advantages:

**Token efficiency**: context grows only where needed. If the task is "create a PR with this diff", the model uses 3-4 commands. It doesn't load documentation for all 200 `gh` commands.

**Unix composability**: CLIs compose. `git log --oneline | grep "fix" | head -20` is a powerful operation combining three tools. With MCP, the same result would require separate calls or a dedicated tool.

**Natural debugging**: when a command fails, the error output is text. The model reads it, understands, corrects. With MCP, errors pass through an extra layer of abstraction.

**Zero infrastructure setup**: a CLI skill is a text file documenting how to use an already-existing tool. An MCP server is a service to deploy, maintain, and monitor.

---

## The progressive discovery pattern

This is the most underrated aspect of CLI skills, and it's worth dwelling on.

A developer who doesn't know a tool doesn't read the 300-page manual before starting. They type the command, read the help, try, fail, try again. The feedback loop is fast and contextual.

LLMs can do the same thing — and they should.

A well-written skill is not an encyclopedic dump of documentation. It's a starting point:

```
# terraform skill
Use `terraform` to manage infrastructure as code.
Entry point: `terraform --help` to discover subcommands.
Common pattern: init → plan → apply.
For details on a subcommand: `terraform <subcommand> --help`.
```

The model will start from this base and *build* understanding of the tool during execution, exactly like a junior developer in their first sprint with a new technology.

This directly contrasts with the MCP approach, where all tools must be declared upfront in the server schema — the model knows everything from the start, but pays for that "everything" in tokens on every call.

---

## A practical decision matrix

| Criterion | MCP | CLI Skill |
|---|---|---|
| Non-textual external system (graphics, audio, BI) | ✓ | ✗ |
| OAuth authentication / complex sessions | ✓ | Depends |
| Tools already available as CLI | ✗ | ✓ |
| Limited token budget | ✗ | ✓ |
| Small team, zero infrastructure to manage | ✗ | ✓ |
| Structured audit trail required | ✓ | Partial |
| Unix pipe composability | ✗ | ✓ |
| Enterprise SaaS system integration | ✓ | ✗ |

---

## The hybrid case: you don't have to choose

In a mature professional coding workflow, the right answer is often hybrid:

- **MCP** for integrations with external systems that genuinely require it (the design system in Figma, notifications in Slack, deploys on platforms with complex APIs)
- **CLI skills** for the entire development toolchain: git, Docker, kubectl, terraform, test runners, linters, package managers

The key point is not to use MCP out of laziness (because "it's more modern") or CLI skills out of frugality (because "it's simpler") — but to choose based on the nature of the system being integrated and the real token cost of each interaction.

---


MCP and CLI skills are not in competition — they solve different problems.

MCP is powerful when you need to bring the model into the territory of systems that don't speak text: graphical systems, creative platforms, SaaS services with complex state. It's the only sensible way to do things like "generate a Canva presentation from my README."

CLI skills are gold in everyday professional coding, where tools are already excellent, already composable, already battle-tested by decades of Unix philosophy — and where every unused token is money saved and latency reduced.

Progressive CLI discovery, moreover, is not a limitation: it's a feature. It teaches the model to reason like a good developer — starting from the bare minimum and building understanding only where needed.
