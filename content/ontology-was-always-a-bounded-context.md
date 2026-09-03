---
title: "The Ontology Was Always a Bounded Context"
date: 2026-09-01 09:56
tags:
- AI
- LLM
- ontology
- DDD
- agents
- MCP
category: AI
author: samreghenzi
description: "Agentic AI is rediscovering ontologies as the fix for multi-agent chaos. Domain-Driven Design solved this exact problem twenty years ago, and it didn't need a global schema."
slug: ontology-was-always-a-bounded-context
---

Two agents meet in a park.

"I've just had a complaint from a customer," says the first.

"What's a customer?" asks the second.

"Anyone with an account."

A third agent walks over.

"That's not a customer," it says. "A customer is anyone with an active subscription."

The three agents pause.

Nobody is wrong. Nobody is hallucinating.

They are just using the same word to mean different things.

And somewhere between them, an integration is about to break.

![Three agents in a park, each defining "customer" differently](/images/xkcd_style_agents_customer_en.png)

This is the failure mode that is currently being rebranded as "agents need ontologies." The diagnosis is right. The fix being marketed alongside it is not. That fix is a single shared ontology sitting above the agents, arbitrating meaning for everyone — and it's the wrong prescription for a problem that already has a name and a twenty-year-old solution. The name is Domain-Driven Design. It isn't showing up in this conversation because most of the people having it came from data and knowledge graphs, not from software architecture.

## The problem is real and it's measurable

Start with the evidence, because the failure isn't hypothetical. OG-RAG, presented at EMNLP 2025, anchors retrieval to an ontology-backed hypergraph instead of a flat vector index. It reports a 55% jump in fact recall and 40% in answer correctness over standard RAG on the same corpus. A 2026 biomedical study went further. Grounding agent outputs against a domain ontology in RDF/OWL brought hallucination rates on clinical queries down from 63% and 48%, depending on the baseline, to 1.7% — with accuracy around 98%.

Numbers like that explain why every vendor with a graph database is suddenly an "ontology for agentic AI" company. They also explain why the instinct isn't wrong. Give an LLM-based system an explicit, checkable model of the domain it operates in, and it gets measurably more reliable. I made a version of this argument in [The Guardrail Is Not in the Model](/ontologies-agentic-guardrails.html): the check that catches an illegal state has to live outside the model, because a probability distribution cannot reliably remember a rule that was never written down.

What that post didn't answer is the next question, which is organizational rather than architectural. Whose ontology? Covering what? Owned by whom, and updated how? That's where the current wave of enterprise ontology platforms gives an answer I don't think holds up.

## The diagnosis that keeps being wrong

The answer on offer — from Palantir's Foundry Ontology to Stardog to RelationalAI — is some version of: build one semantic model of the enterprise, wire every agent to it, and let it be the shared source of truth.

I have seen this movie. It's the Semantic Web, 2001 to roughly 2010, W3C-flavored instead of venture-flavored. RDF, OWL, a vision of universally linked data with formally specified meaning. Then a slow, expensive collapse. The reason it failed was never that formal semantics don't work; SHACL validators are boring, cheap, and effective at exactly the scale you point them at. It failed because getting an organization to agree on one model of everything is brutally expensive, and keeping that model true over time is worse.

The new version does have one genuinely different cost: authoring. An LLM can draft a plausible ontology from your documentation and schemas for a few cents, where a knowledge engineer used to bill for weeks. That's real progress. But authoring was never the part that killed the Semantic Web. Governance was — what happens once two teams' understanding of "customer" starts to drift apart in production. Cheaper to build is not the same as cheaper to own, and owning is where a global ontology dies.

## DDD already named this problem

Here is what the ontology-for-agents conversation is missing: this is not a new problem. Eric Evans described it in *Domain-Driven Design* in 2003 — different parts of an organization using the same word to mean different things. His answer was never "build one model and force everyone onto it."

His answer was the **bounded context**: a model only has to be internally consistent within an explicit boundary. Inside the billing context, "customer" means "entity with an active subscription," full stop, and every rule is coherent under that definition. Inside the support context, "customer" means "entity with an account," and that's equally coherent on its own terms. The two contexts are not wrong relative to each other. They were never supposed to share a definition in the first place.

The **ubiquitous language** maps directly onto what an ontology actually is when it's working. It's not a separate artifact that sits above the code and gets synced with it by a process nobody enjoys. It *is* the vocabulary the domain experts and the model use, inside that one context, for that one purpose. An ontology that lives outside the bounded context it describes is exactly the kind of artifact DDD spent a book telling you not to build.

And when two contexts genuinely need to talk, DDD already has the vocabulary for that too. A **shared kernel** for the small slice of model both sides agree to co-own. An **anticorruption layer** when one side must consume the other's model without importing its assumptions. A **partnership** when two teams agree to evolve their contexts in step. Read the current papers on "multi-agent semantic interoperability" and you are reading context mapping with the serial numbers filed off.

## Event-driven architecture already named the other half

Bounded contexts keep a local model coherent. They don't explain how contexts stay in sync without collapsing back into one shared schema. That half was solved by event-driven architecture.

The core discipline is treating an event as a fact, not a command: `OrderPlaced`, not `PlaceOrder`. A command presupposes that the receiver shares your model closely enough to know what to do with the instruction. A fact just asserts that something happened, in the vocabulary of the context that emitted it, and lets every consumer interpret it inside its own model. That is far looser coupling than a synchronous call between two agents that must agree, in real time, on one shared schema just to complete a request.

Event sourcing covers the other thing the enterprise-ontology pitch leads with: audit and accountability. A well-designed event log is already a complete, ordered, immutable record of every fact the system has asserted. That is precisely the traceability that Palantir and Stardog sell as the differentiated value of an ontology layer. You don't need a global semantic model to get an audit trail. You need an event log that nobody is allowed to mutate.

Which makes it a little dispiriting to watch the current agent stack rebuild what event-driven architecture spent twenty years moving away from. MCP, launched by Anthropic in late 2024, is a good protocol for what it does: a stable way for a model to discover and call a tool. But the pattern forming on top of it — and on top of LangGraph, CrewAI, and AutoGen — is a central orchestrator calling each agent synchronously, with a shared understanding of the payload assumed on both ends. Distributed systems spent two decades learning to prefer choreography over that. The agent stack is reinventing the thing we walked away from.

## Explicit structure isn't a compromise, it's a multiplier

There's an objection worth taking seriously here: agents aren't microservices. A microservice's behavior is deterministic given its inputs; an LLM's isn't. Doesn't imposing a rigid schema on an inherently stochastic process miss the point?

It's the opposite. Precisely *because* the output is stochastic, giving it an explicit shape to land in is what makes it usable. This isn't hand-waving — it's what the numbers at the top of this post already showed. Constraining generation against an explicit ontology is what took the biomedical hallucination rate from the 50-60% range to 1.7%. Structure doesn't fight the model's nature; it compensates for it. A type system doesn't fight a language's flexibility either. It gives the parts that need to be reliable somewhere firm to stand.

There's a second benefit that's easy to undersell: introspection. An explicit, local ontology gives you a place to *look* when an agent's behavior needs explaining, in a way a free-text prompt never does. When an agent inside the billing context takes an action, you can ask which entities and relations it reasoned over, and check the answer against a schema — instead of re-reading a transcript and guessing. That extends the argument from [The Guardrail Is Not in the Model](/ontologies-agentic-guardrails.html) one step further. The structure that lives outside the model isn't only a cage that stops bad states. It's an instrument that makes the good ones legible.

## Who maintains it: the review loop, not the curator

The objection that actually matters is the one that killed the Semantic Web: someone has to own this thing over time, and ownership is expensive. DDD's answer was never "write the model once." A mature bounded context goes through *model refinement* as the team's understanding deepens. The ubiquitous language evolves because the domain does, not because someone forgot to finish it the first time.

What's different now is who drafts the refinement. In the expert-systems era, and in the Semantic Web's, a human had to notice the drift, understand it, and hand-author the fix. Today the agent itself can be the one to notice. It can flag the cases where its actions kept getting rejected by the local schema, or where two contexts' events stopped lining up, and propose a specific, scoped patch to the local ontology. A human still reviews and merges the diff. What disappears is the step where a person has to notice the drift unassisted and draft the fix from a blank page.

Note the constraint doing the work here: the patch is scoped to one bounded context, not to a global model. That's what keeps the loop tractable. This is a real reduction in the maintenance cost that killed the last two attempts at formal semantics, and it only exists because the thing being maintained is small.

## The provocation

None of this requires a new discipline called "ontology engineering for agentic AI." It requires applying to agents the discipline distributed systems already have. Give each agent a bounded context and an explicit local model, not a slice of a shared global one. Connect contexts with events that are facts, not commands that presuppose a shared schema. Run a periodic, LLM-assisted refinement loop instead of pretending the model will be right forever once you've paid to build it.

So before buying a platform that sells itself as "the enterprise ontology layer for your agents," ask a blunter question: is the missing piece really a new epistemic layer, or is it a bounded context design, an event bus, and a review process you haven't built yet? In most of the failures I've seen, it's the second one. And it was always going to be cheaper.
