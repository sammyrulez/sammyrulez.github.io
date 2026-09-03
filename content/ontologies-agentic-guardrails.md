---
title: "The Guardrail Is Not in the Model"
date: 2026-08-30 14:16
tags:
- AI
- LLM
- ontology
- agents
- python
- claude
category: AI
author: samreghenzi
description: "Agent failures are usually not hallucinations — they are illegal states nobody wrote down. Why the fix belongs outside the model, and how a formal ontology becomes a real guardrail."
slug: ontologies-agentic-guardrails
---

Frank Coyle gave [a twenty-minute talk](https://www.youtube.com/watch?v=Sir59K8ZDPU) at the AI Engineer World's Fair that has been circulating for a few weeks now, and the argument in it is simple enough to state in one sentence: agentic systems need ontologies, because LLMs are probabilistic and probabilistic systems need logical guardrails.

I think he is right, but the interesting part is why, and that is easier to see if you start from the failures rather than from the ontologies.

## The failure that isn't a hallucination

Take a support agent that handles refunds. A request comes in, the agent reads the order, calls the payments tool, and refunds €340 to the customer. The tool call is well-formed, the arguments validate, and the summary it writes afterwards is an accurate description of what it did. The problem is that the same order had already been refunded four days earlier.

It is worth going through the layers that should have caught this, because none of them did. The model did not hallucinate, since it never stated anything false. Schema validation passed: the amount was a positive decimal, the order ID was a UUID, and the reason was one of the allowed values. The eval suite passed too, because it scores the agent's output for helpfulness and faithfulness, and as a piece of text the response was fine. The system prompt did say not to issue duplicate refunds, and the model would have confirmed that rule if you had asked it.

The failure was not in the language. It was that "an order has at most one refund" is a rule of the business that existed only in the heads of a few engineers and in the implicit assumptions of some older database queries. It was never written down anywhere a machine could check it.

Most agent incidents I have seen have this shape. They are not fabrications, they are illegal states that nobody had written down. A payout goes to a support rep instead of the buyer because the recipient field was typed as a string. An order ends up with the status `probably_shipped` because the tool accepted free text. A category becomes its own ancestor because nothing said the relation was acyclic.

The usual responses to this all have something in common. Longer system prompts, more context, better retrieval, another round of fine-tuning: every one of them is a change inside the model, and every one asks a probability distribution to reliably avoid a state that was never defined. It is an attempt to solve a logical problem with more probability.

## The loop is where the power and the risk both come from

There is a point in Coyle's talk that puts this in a useful frame.

In 1966 Böhm and Jacopini proved that any language with three constructs — sequence, conditional, and iteration — can compute anything computable. The then-current argument about whether Fortran or COBOL was the better language was therefore beside the point, since both had all three.

Until recently an LLM call gave you sequence and, with tool use, something like a conditional. Then we added the loop, in the form of `while stop_reason == "tool_use"`. That third construct is a large part of why agents can now do things that a 2023 chat interface could not.

Along with the power we inherited the familiar problems of loops. They can fail to terminate. They can drift, with small errors compounding so that each turn is slightly further from the goal than the last and no single step looks wrong. They can consume an unbounded amount of money, which is why token budgets exist.

So we have a Turing-complete system whose transition function is a neural network, operating over a state space that was never formally specified, and our main way of constraining it is a system prompt written in English.

That is not a criticism of LLMs. It is the same reason we do not secure a web application by asking people in the documentation not to attempt SQL injection. A constraint that the system has to pass through is different in kind from a constraint the system is asked to remember.

## What an ontology is, in practical terms

The word carries a lot of philosophical history, from Aristotle's categories through Quine to the Semantic Web work of the 2000s. Coyle sensibly reaches for Gruber's 1993 definition, *a formal specification of a shared conceptualization*. For engineering purposes it can be made more concrete than that.

The first part is a **graph**: entities, the relations between them, and properties on both. Order, Customer, Refund, SupportRep, `refundOf`, `paidTo`, `status`. If you have ever drawn your domain on a whiteboard, you have already done most of this work.

The second part is a **set of constraints that sits beside the graph** rather than inside it. This is the part that usually gets skipped, and it is where most of the value is. Graph technology lets you state things about the shape of the graph and then check them mechanically: that `status` takes one of exactly three values, that an Order has at most one Refund, that the recipient of a payout must be a Customer and that nothing is ever both a Customer and a SupportRep, that `parentCategoryOf` is transitive so a category cannot end up inside itself.

Some of these statements let you **derive** facts that were never written down. If the source of `teaches` is always a Teacher, then the single assertion "Bob teaches Scooter" tells you that Bob is a teacher and Scooter a student without either being stated. Other statements let you **reject** a state. Both are useful, and they are not the same operation, which matters later.

The structural point is that these rules live neither in the data nor in the weights. Not in the rows, because a relational schema can express a foreign key but not "at most one refund per order across these three tables." Not in the model, because fine-tuning adjusts a distribution rather than adding a decision procedure. They live in a third place, and that third place can be checked cheaply by ordinary code.

That is the architectural argument. The rest is implementation.

## This has been tried before

If this sounds familiar, it should. It was tried in the 1980s and it failed.

Symbolic AI then meant expert systems: knowledge engineers sitting with domain experts, extracting rules and encoding them by hand. A lot of money went into it, Japan launched the Fifth Generation project, and then the field collapsed into the AI winter. The usual summary is that it did not scale.

Coyle mentions this and moves on, but the reason it did not scale is worth pausing on, because it determines whether we are about to repeat the mistake.

Expert systems did not fail because formal logic is useless. They failed at knowledge acquisition. The bottleneck was a person translating a domain expert's tacit knowledge into rules, one rule at a time, and then maintaining those rules as the domain changed underneath them. The reasoning was the cheap part. Getting the knowledge in was the hard part.

That is precisely the part that has changed. An LLM is good at reading unstructured material — tickets, documentation, transcripts, code, schemas — and proposing structure from it. A validator is good at the thing LLMs are bad at, which is saying no reliably.

So the division of labour has swapped. In 1985 humans did the acquisition and machines did the inference. Now the model does the acquisition and the machine does the verification, with humans reviewing a diff rather than authoring a corpus. That is a different bet from the one that failed.

There is a cost that tends to go unmentioned, though: someone has to own the ontology. When the business introduces partial refunds, "at most one refund per order" stops being true, and if nobody updates the rule the guardrail starts blocking legitimate work. A stale ontology is worse than no ontology, because it fails on correct behaviour and the team learns to route around it. This is a schema, and schemas need owners and a migration process.

## Where it goes in the loop

Here is the agentic loop, with the place for the check marked.

```python
import anthropic

client = anthropic.Anthropic()
messages = [{"role": "user", "content": user_request}]

while True:
    response = client.messages.create(
        model="claude-opus-5",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        tools=TOOLS,
        messages=messages,
    )

    if response.stop_reason != "tool_use":
        break

    messages.append({"role": "assistant", "content": response.content})

    results = []
    for block in response.content:
        if block.type != "tool_use":
            continue

        # 1. Shape. Pydantic at the door: is this even the right type?
        try:
            args = TOOL_MODELS[block.name].model_validate(block.input)
        except ValidationError as e:
            results.append(error_result(block.id, f"Invalid arguments: {e}"))
            continue

        # 2. Effect — computed, NOT committed. Pure function, no side effects.
        proposed = TOOL_IMPLS[block.name].propose(args)

        # 3. Legality. The ontology at the ledger: is this state allowed?
        verdict = ontology.check(proposed.as_triples())
        if not verdict.ok:
            results.append(error_result(block.id, verdict.explain()))
            continue

        # 4. Only now does anything leave the process.
        results.append(ok_result(block.id, proposed.commit()))

    messages.append({"role": "user", "content": results})
```

Coyle has a good way of summarising this: Pydantic at the door, the ontology at the ledger. The two answer different questions. Pydantic asks whether the arguments have the right shape, so that a decimal appears where a decimal belongs. The ontology asks whether the resulting state is legal, and that question can only be asked about the proposed effect rather than the arguments. This is why step 2 has to be a pure function. An agent that writes to the database and then validates has already lost the ability to refuse; the check has to happen while the action is still a hypothesis.

The other thing worth noting is what happens on rejection. The verdict goes back to the model as a tool result together with an explanation, so the agent is told that its move was not allowed and why, and it takes another turn. Nothing crashes. If the same rejection repeats, escalate to a human.

The validator itself is short:

```python
from rdflib import Graph
from pyshacl import validate

DOMAIN = Graph().parse("shop.ttl", format="turtle")           # the graph itself
SHAPES = Graph().parse("shop-shapes.ttl", format="turtle")    # the constraints

def check(proposed_triples: Graph) -> Verdict:
    # Merge the proposed effect into the domain graph and ask whether the
    # result is a legal world. Nothing here touches the database.
    g = DOMAIN + proposed_triples
    conforms, _, report = validate(g, shacl_graph=SHAPES, advanced=True)
    return Verdict(conforms, report)
```

```turtle
# shop-shapes.ttl
:OrderShape a sh:NodeShape ;
    sh:targetClass :Order ;
    sh:property [
        sh:path :status ;
        sh:in ( "paid" "shipped" "refunded" ) ;   # kills probably_shipped
        sh:maxCount 1 ;
    ] ;
    sh:property [
        sh:path [ sh:inversePath :refundOf ] ;
        sh:maxCount 1 ;                            # kills the second refund
        sh:message "Order already has a refund." ;
    ] .

:PayoutShape a sh:NodeShape ;
    sh:targetClass :Payout ;
    sh:property [
        sh:path :paidTo ;
        sh:class :Customer ;         # kills the payout sent to a support rep
        sh:minCount 1 ;
        sh:maxCount 1 ;
    ] .
```

This is where the distinction between deriving and rejecting starts to matter, because most graph tooling was designed for the first of the two.

Graph technology grew up on the open web, where a graph is partial by construction: you hold a fragment of something larger, and the absence of a fact means unknown rather than false. Reasoners built on that assumption are generous. Tell one that an order can have at most one refund and then assert two, and it will not complain. It will conclude that the two refunds must be the same refund. That is sound reasoning under the assumption it was given, and it is the wrong answer here.

A refund ledger is the opposite kind of graph. It is closed and complete, and absence does mean false: if a second refund is not in it, there is no second refund. What you want for that is constraint validation rather than inference — cardinality, permitted values, required types — checked against a graph you have declared to be complete. That is what the shapes above do, and it is why the validator is short and contains no reasoner. Validation also produces a structured violation report, which is exactly what you want to hand back to the model as a tool result.

Inference is still useful for other things: transitive closure over a hierarchy, deriving types you did not assert, surfacing a contradiction you would not have thought to query for. Treat it as a second layer, added deliberately. The check that stops the duplicate refund is the validator, so if you build only one of the two, build that.

It is also worth not starting from scratch. `schema.org` has a substantial vocabulary for commerce, people and events, and reusing it means your ontology carries meaning outside your own codebase.

## What this does not fix

An ontology does not make the agent smarter. It reduces the set of actions the agent can take without being stopped. Those are different properties, and the second one is the one you can verify.

It catches illegal states, not mistakes of judgment. A refund of €340 that should have been €34 is entirely legal: right type, right recipient, no duplicate, valid status. The ontology has nothing to say about it, and the same is true of a decision to refund a customer who was not entitled to one. Every constraint you can write down is a constraint you already knew, so the guardrail covers exactly as much as your explicit knowledge and no more.

That gives a reasonable scoping rule. If your domain has no constraints you can write down, this layer is not for you. A summarisation agent, a research assistant or a code explainer has no ledger and no illegal state, so validation only adds latency and maintenance. The technique is worth the effort where the agent moves money, changes records, sends things to people or drives a state machine — that is, where "wrong" has a definition that survives being written down.

That is a smaller set than all agents, but it is close to the set of agents people are currently trying to put into production.

The neuro-symbolic framing is fashionable, and I am generally wary of it because it usually arrives as an architecture diagram rather than as a claim you can test. The practical version is more modest: write down the rules of your domain in a form a machine can check, put the check between the agent's intent and its effect, and stop relying on the model to remember them.
