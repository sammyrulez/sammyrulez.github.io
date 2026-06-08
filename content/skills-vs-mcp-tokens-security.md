Title: Skills vs MCP Servers: The Hidden Cost of Tools in LLM Workflows
Date: 2026-06-07
Category: AI
Tags: llm, mcp, skills, claude, tokens, security
Slug: skills-vs-mcp-tokens-security
Author: Sam Reghenzi
Summary: Why CLI-based skills are often cheaper, safer, and more ergonomic than MCP servers — and the one case where MCP genuinely wins.

When you start wiring a language model into real work, you quickly discover that the choice of *how* it reaches the outside world is not a detail. It is the single decision that drives token bills, latency, security posture, and — perhaps most underrated — how much configuration pain your team is signing up for.

Two approaches dominate today: **MCP servers** and **skills**. They look similar on the surface (both give the model "tools"), but they sit on opposite ends of almost every meaningful axis. Understanding where each one shines is the difference between an assistant that feels like a colleague and one that feels like a very expensive intern who keeps forgetting where the kitchen is.

## The token tax of MCP

An MCP server is, at its core, a contract. It exposes a list of tools, and for each tool it must declare — *upfront, at the start of every interaction* — a precise description of what the tool does, the shape of its parameters, and the structure of the data it returns. This is what makes MCP feel so clean from a software-engineering perspective: it is strongly typed, self-documenting, schema-first.

But that beauty has a price, and the price is paid in tokens.

Every tool description, every parameter docstring, every return-type schema gets loaded into the context window the moment the conversation begins. The model has to "see" the whole catalogue before it can decide what to do — even if, in the end, it only uses one tool out of forty. And it pays that cost again on every turn, because the tool definitions live in the context.

Connect three or four MCP servers — say a Jira server,  Slack , Github !!! — and you can easily burn ten or twenty thousand tokens *before the user has even typed a question*. That is not an exaggeration: it is the normal operating condition of a richly integrated MCP setup. And the configuration side is rarely ergonomic either: each server wants its own JSON block, its own credentials, its own lifecycle, its own quirks about transport and authentication.

## Skills work the way developers actually work

A skill, by contrast, is closer to how a human engineer approaches an unfamiliar tool. You don't read the entire `git` manual before your first commit. You type `git --help`, then `git commit --help` when you need it, and you progressively build a working mental model of just the parts that matter for the job in front of you.

A well-designed skill encodes exactly that posture. It tells the model: *here is a CLI, here is the entry point, here is the philosophy — explore it when you need it.* The model then uses the existing command-line tool, discovers flags on demand, and only pays for the surface area it actually touches.

The implications are significant:

- **Tokens scale with the task, not with the catalogue.** If the work needs three `gh` subcommands, you pay for three subcommands. The other 197 stay invisible.
- **The CLI already exists.** No server to deploy, no schema to maintain, no transport to debug. You are reusing decades of Unix engineering.
- **Composition is free.** Pipes, redirects, `xargs`, `jq` — the model inherits all of it. With MCP, every composition has to be modeled as a new tool or chained call.

## The security angle nobody talks about

There is a second, quieter advantage of skills over MCP that I think deserves more attention: **security**.

When a skill drives a CLI, it inherits the security model of the host operating system. The command runs as the local user, with that user's permissions, against that user's keychain, SSH agent, `~/.aws/credentials`, `gcloud` session, `kubectl` context — whatever credential machinery is already in place and already audited by your IT and your habits. There is no extra surface to attack, no new long-lived token to rotate, no new daemon to keep patched.

MCP servers, by their nature, want their own configuration. They often need their own copies of credentials, their own auth flows, their own way of holding state between calls. That is not inherently insecure — many MCP servers are written carefully — but it is *additional* surface area. Every new MCP server is a new place where a secret can leak, a permission can be misconfigured, or a vulnerability can hide. A skill that wraps `aws` or `kubectl` adds zero new credentials to your laptop. An MCP server for AWS adds at least one.

For teams that already have a mature CLI-based security story — and most engineering teams do, even if they don't think of it that way — skills give you tool access for free, on top of a model the security team has already reviewed.

## A controversial case: connecting to MySQL

I want to be honest about where this argument breaks down, because it taught me something.

Recently I needed an assistant to work against a MySQL database. The "skill" route was obvious: just let it use the `mysql` CLI. It is well-known, secure, and uses the system's own credential files. Clean, ergonomic, almost no setup. I expected it to be the clear winner.

It wasn't. Or at least, not unambiguously.

The CLI approach turned out to be *slow* and *token-hungry* in a way I had not anticipated. Every query opened a new client session — connecting, authenticating, executing, tearing down. The result came back as raw text, which the model then had to re-parse on every step, often re-issuing similar queries just to confirm the shape of what it had already seen. For analytical work involving many sequential queries, this was painful.

The MySQL MCP server, on the other hand, kept a **connection pool** open. It pre-processed the result set into a structured form the model could consume without re-tokenising whole tables. It dramatically reduced the per-query overhead, both in latency and in tokens. For that specific workload — many small queries against the same database, in the same session — MCP was genuinely the better tool.

The lesson is not "MCP wins after all." The lesson is more interesting: **MCP is worth its overhead when it provides something the CLI fundamentally cannot — persistent state, structured pre-processing, server-side intelligence**. A `mysql` CLI invocation is stateless by design; it cannot pool connections or cache schema metadata across calls. The MCP server can. That capability gap, not the schema cleanliness, is what justifies the cost.

So the honest rule is: prefer skills by default, but reach for MCP when the integration *needs* state, pooling, binary assets, OAuth dances, or any other capability that a single CLI invocation genuinely cannot offer. Not because MCP is more modern, not because the schema is prettier — because the workload demands persistence the shell cannot give you.

## Where MCP is the obvious answer: complex, non-textual systems

The MySQL story is the *subtle* case. There is also a much more obvious one, and it is worth naming explicitly: systems that simply do not live in text.

Think of **Excalidraw**, **Canva**, **Figma**, a 3D scene editor, a video timeline, a BI dashboard builder. These platforms are not just "an API with some commands" — they are spatial, visual, stateful environments. A shape on a canvas has coordinates, layers, z-order, parent groups, bindings to other shapes; a Canva design has templates, brand kits, asset libraries, page hierarchies. None of that maps cleanly to a stream of bytes flowing through a pipe.

For these systems, the CLI story falls apart for reasons no amount of cleverness can fix:

- **There is no good text representation.** You cannot meaningfully describe "the element 40 pixels to the right of the title, snapped to the grid, grouped with the icon" in shell flags.
- **State is essential.** The user (or the model) is working *inside* an open document, not invoking one-shot commands. Selection, focus, undo history, currently active tool — all of this is context that needs to live somewhere.
- **Binary and structured assets dominate.** Images, fonts, embedded media, vector primitives. A CLI can shuffle files around; it cannot reason about a layout.
- **Round-trips need to be cheap.** Adding a node, moving it, re-styling it, and reading back the result needs to feel like a conversation with the canvas, not a series of full re-renders.

An MCP server for Excalidraw or Canva is in its element precisely here. It can hold the document open, expose primitives that match the *concepts* of the tool (create node, connect nodes, set fill, group selection), and let the model think in the vocabulary of the platform instead of in the vocabulary of `bash`. The token cost of the schema, which felt extravagant for a database CLI, suddenly looks like a bargain when the alternative is "describe a whiteboard over stdout."

In other words: the more a system departs from the Unix philosophy of "everything is text," the more MCP earns its keep. For canvases, design tools, creative software, and rich SaaS environments with their own native object models, MCP is not a luxury — it is the only honest way to bridge model and tool.

## The epic conclusion

There is a beautiful symmetry in all this. We spent decades building Unix into one of the most quietly powerful platforms in computing: composable, scriptable, securable, observable, and — crucially — *cheap*. Every command-line tool is a small, hard-won monument to clarity. Every credential file, every SSH key, every IAM role represents years of organisational learning about how to keep secrets in the right hands.

Skills let language models stand on that mountain.

They let the model behave like a thoughtful new hire who reads the help text, asks the system what it can do, and uses the credentials already sitting on the laptop — no new servers, no new secrets, no new schemas, no new tax on every token of context. They scale down to nothing when unused and up to everything when needed. They are, in the deepest sense, *aligned with the grain of the system they run on*.

MCP, in turn, becomes what it should always have been: not the default front door for every integration, but the specialist tool for the cases where text and shell are genuinely insufficient — when you need to render a slide, drive a design canvas, hold an OAuth session, pool a database connection, stream binary assets through a protocol the terminal was never meant to carry.

The choice is no longer "which protocol is more elegant." It is the older, harder, more interesting question that good engineering has always asked: *what is the smallest, cheapest, safest thing that will actually do the job?*

For most of what we ask language models to do every day, the answer was sitting in `/usr/local/bin` the whole time.
