---
title: "Typed Judgments or Agentic Loops? Benchmarking Jev Against a GPT Agent"
date: 2026-09-21 18:20
tags:
- AI
- LLM
- typesafe
- benchmarks
- agents
category: blog
author: samreghenzi
description: "A real migration from an agentic classification loop to TypeSafe's Jev: 7x faster and 56% fewer calls at volume, but the agent still wins where backtracking matters."
slug: typesafe-jev-vs-agentic-loop
---

I spent last week replacing an agentic pipeline with something that isn't an agent at all, and then measuring what I had actually traded away. The task is product classification: take a product description, walk down a category taxonomy (Amazon, Shopify), and land on a leaf node.

The old pipeline was the shape everybody builds in 2025. An LLM agent on `gpt-5.2` descends the tree by calling tools, one level at a time, keeping the conversation history. A second LLM acts as a judge on the final path: if it rejects the result, the descent restarts from the top.

The new one has no loop and no judge. Every level of the tree is a typed `Choice` question to TypeSafe's System One model — **Jev** — which returns a probability distribution over the options instead of text. The judgment is no longer a call: it's a function of those probabilities.

Same 50 products, same taxonomies, same Postgres, real models on both sides. Here's what came out.

## The numbers, up front

| Per classification | Agentic | Jev / TypeSafe | Δ |
|---|---|---|---|
| Mean latency | 9.62 s | 1.38 s | −86% |
| Median | 8.55 s | 1.37 s | −84% |
| p90 | 13.70 s | 1.91 s | −86% |
| Max | 19.30 s | 3.68 s | −81% |
| Per single call | ~1.30 s | 0.43 s | −67% |
| Model calls | 7.22 | 3.18 | −56% |
| Total tokens | 8,380 | 5,400 | −36% |
| Levels reached | 3.60 | 3.62 | ≈ |

The distributions don't overlap anywhere: **the worst of the 50 runs on Jev (3.68 s) is still faster than the best run of the old pipeline (5.50 s)**. Fifty products, run sequentially, finish in 68.8 seconds of wall clock.

Two mechanisms explain almost all of it. First, a System One response takes 0.43 s against 1.3 s for an agentic turn — there is no text to generate, only a distribution to return. Second, **speculative fan-out**: the same request carries the question about the current level *and* the questions about the children of each candidate, so the descent drops two levels for the price of one call.

An honesty note that matters: the old benchmark ran with 5 threads in parallel, the new one sequentially. Contention and possible upstream throttling may have inflated the old numbers, so the 7x headline is probably generous. The per-call gap — 1.30 s vs 0.43 s — doesn't depend on concurrency, and that one is solid.

One thing worth watching is the token profile flipping over. The agentic pipeline was 96% input: it re-sent the whole history every turn and generated a handful of words. Jev inverts it — output tokens grow 383%, because every `Choice` returns a probability per criterion and wide levels have dozens of criteria. If TypeSafe ends up pricing output well above input, the way OpenAI does, that 36% token saving thins out fast.

### Fan-out is free, and it doesn't change the answer

I ran a controlled A/B on eight stratified products, fan-out on (threshold 8) and off. The question was whether speculative questions — the ones about branches that get discarded — cost in latency what they save in calls.

| Questions in one request | 1 | 4 | 5 | 7 |
|---|---|---|---|---|
| Response time | 0.37 s | 0.39 s | 0.32 s | 0.36 s |

Response time is flat in the number of questions. Independent questions are evaluated in parallel and cost, in time, what one costs. Net effect: −12% time, −11% calls, +25% tokens. And the result that matters more than those three numbers: **all eight paths are identical between the two configurations**. A speculative question — asked without knowing whether that branch will be taken, with the premise declared in the instructions — gives the same answer as the direct one. That's the correctness condition the whole mechanism rests on, and it holds.

## Where Jev is the right call

If you squint at those tables, the case writes itself. **Jev wins decisively when you have volume, and when time and cost are hard constraints.**

At 1.38 s per item with a 0.55 s standard deviation, classification stops being a batch job and becomes something you can put in a request path. Half the calls and a third fewer tokens means the unit economics survive contact with a catalog of hundreds of thousands of items rather than fifty. And the tail is what really changes the operational story: p90 at 1.91 s, worst case at 3.68 s, against an agentic worst case of 19.3 s. You can put an SLA on a distribution that narrow. You cannot put one on a loop whose length is decided by a judge model.

There's a subtler win hiding in the difficulty breakdown:

| Group | n | Agentic | Jev |
|---|---|---|---|
| clear | 40 | 8.94 s | 1.45 s |
| ambiguous | 2 | 8.95 s | 1.26 s |
| italian | 3 | 11.10 s | 1.05 s |
| vague | 2 | 13.05 s | 0.87 s |
| out-of-taxonomy | 2 | 14.90 s | 0.75 s |
| adversarial | 1 | 16.50 s | 1.78 s |

The old pipeline got *slower* exactly where it was least sure of itself. An out-of-taxonomy product cost 14.9 s to land in the wrong place anyway: the judge rejected, the descent restarted, the budget ran out. With Jev those cases are among the fastest, because the descent stops early and nobody restarts it.

Read that twice, though. It's a time saving that is also a renunciation.

## Where the agentic loop still earns its cost

Comparing the assigned paths on the same 50 products: 36 identical (72%), 2 where one is a prefix of the other, **12 divergent**. On the fourteen non-identical cases I judged by hand — one annotator, no ground truth, so treat it as a signal and not as an accuracy measurement — the tally is 5 to Jev, 4 to the agent, 4 I can't honestly call either way, and 1 where both are wrong.

The pattern in those disagreements is the interesting part, and it splits cleanly. Here are the fourteen, with my call on each:

| Product | Agentic | Jev | Better |
|---|---|---|---|
| windbreaker (described in Italian) | `Clothing, Shoes & Jewelry` | `Sports & Outdoors › Outdoor Recreation › Outdoor Clothing` | Jev |
| MTB helmet | `Sports & Fitness › Accessories` | `Cycling › Helmets & Accessories › Adult Helmets` | Jev |
| leather dog collar | `Pet Supplies › Dog Supplies` | `Pet Supplies › Pet Collars & Harnesses › Standard Collars` | Jev |
| waterproof windbreaker | `Jackets & Coats › Lightweight Jackets` | `Jackets & Coats › Active & Performance › Shells` | Jev |
| 40 L trekking backpack | `Sports & Outdoors` | `Camping & Hiking › Backpacking Packs › Internal Frame` | Jev |
| whey protein powder | `Sports Nutrition › Protein › Powders › Whey` | `Sports & Fitness › Exercise & Fitness` | agentic |
| ceramic mug | `Tableware › Drinkware › Mugs` | `Kitchen & Dining › Food & Beverage Carriers` | agentic |
| USB-C → HDMI adapter | `Computer Accessories › Computer Cable Adapters` | `Laptop Accessories › Chargers & Adapters` | debatable |
| 15-bar espresso machine | `Espresso Machines › Semi-Automatic` | `Espresso Machines › Steam` | agentic |
| OBD2 diagnostic scanner | `Tools & Equipment › Diagnostic, Test & Measurement` | `Car Electronics & Accessories › Car Electronics` | debatable |
| cotton baby bodysuit | `Clothing › Baby & Toddler Clothing` | `Baby & Toddler` | agentic |
| 16″ kids' bike | `Cycling › Kids' Bikes & Accessories › Kids' Bikes` | `Toys & Games › Tricycles, Scooters & Wagons › Kids' Bikes` | debatable |
| generic gift ("for the person who has everything") | `Gift Cards › Gift Cards` | `Gift Cards` | debatable |
| concert ticket | `Collectibles & Fine Arts › Entertainment` | `Gift Cards` | neither |

Two different failure modes, and they are not symmetric.

**Jev wins where the old pipeline stopped too early.** The Italian windbreaker, the MTB helmet, the dog collar, the 40 L backpack: the agent parked them at `Sports & Outdoors` or `Clothing, Shoes & Jewelry` and gave up. These are *depth* failures, and notice where they came from — three of those four are cases the old judge had explicitly rejected and the loop still failed to fix. The loop had the information, spent the retries (19 of them across the run), and burned the budget without converging. Twelve of the 50 old-pipeline paths were truncated mid-descent when the budget ran out. Agentic descent doesn't just cost more; it degrades under its own cost.

**The agent wins on picking the right branch between two plausible ones.** Whey protein into `Exercise & Fitness` instead of `Sports Nutrition › Protein › Powders › Whey`. A ceramic mug into `Food & Beverage Carriers` instead of `Drinkware`. A 15-bar machine into `Espresso Machines › Steam` instead of `Semi-Automatic`. These are *branch* failures, and they happen at level one or two.

Then there's a third pile, and it's the one I found most informative: **four cases I refuse to score.** Is a USB-C → HDMI adapter a cable adapter or a laptop accessory? Is an OBD2 scanner a diagnostic instrument or car electronics? Is a 16″ kids' bike a bicycle or a toy? Is `Gift Cards › Gift Cards` better than `Gift Cards`? Both answers are defensible, and which one is "right" depends on a merchandising convention that lives nowhere in the product description and nowhere in the taxonomy either. That matters for how you read this whole comparison: **the honest headline is 5–4 with four ties, not a rout in either direction.** A third of the disagreements aren't a model failing, they're the task being underspecified — and neither an agent nor a typed model can resolve that. A labeling guideline can.

That asymmetry is the whole argument. **A depth failure costs you precision; a branch failure costs you the entire subtree.** The mug is not slightly misfiled — it's in a part of the taxonomy where no amount of further descent can recover, because every leaf below `Food & Beverage Carriers` is about thermoses and lunch bags. Once the typed descent commits at level one, correctness at every subsequent level is irrelevant: it's descending inside the wrong world. And the levels where this happens are exactly the widest ones — a first-level choice between dozens of top categories, made on a one-line product description, with the least context available anywhere in the run.

Here's the structural reason the loop is better at this, and it isn't "the agent is smarter." **The information that disambiguates a level-one choice often only becomes available at level three.** Take the kids' bike — a tie on the merits, but a perfect illustration of the mechanism. You can't settle bicycle-vs-toy from the description; you settle it by looking at where the two branches actually lead, noticing that `Toys & Games › Tricycles, Scooters & Wagons` fills up with push-along toys while `Cycling › Kids' Bikes` fills up with geared bicycles, and reasoning backwards from the leaves to the root. A single-pass descent has no mechanism for that: each `Choice` sees its own level, answers, and the answer is final. The agent's loop is, in effect, a search with the ability to *undo* — it can spend a branch, discover it was wrong from downstream evidence, and return the cost. The typed descent is a greedy walk. Greedy walks are fast and they are locally optimal by construction, which is a polite way of saying they cannot recover from an early mistake.

Two more things the loop was quietly buying, both visible in the data:

- **Rejection.** The concert ticket was out-of-taxonomy by design. The old judge rejected 14 paths out of 50; the new `path_score` rejects 1. "This doesn't belong anywhere" is a judgment about the fit between an item and the whole tree — it is not expressible as a confident choice at any single level, because at every single level *something* is the best available option.
- **Stopping at the right height.** The baby bodysuit — and, arguably, the generic gift — show the flip side of the depth story: sometimes the correct answer is a shallower node, and knowing when to stop descending is itself a judgment the loop can make and a per-level `Choice` cannot.

So: on hard, genuinely ambiguous inputs — the ones where the task itself is well posed — the ability to retrace one's own steps produces qualitatively better results, and no amount of latency engineering substitutes for it. What you're paying 9.6 seconds for isn't tool calling — it's search with backtracking, global judgment about fit, and the option to stop early. Most of your traffic doesn't need any of the three. The traffic that does needs all three at once.

The instinct at this point is to hope the confidence score will catch those cases and route them. It doesn't.

### `path_score` measures concentration, not correctness

The LLM judge was replaced by `path_score`: the geometric mean of the edge probabilities along the path, compared against a 0.55 threshold. It costs zero calls. The problem is what it measures.

| `path_score` across the 50 | Value |
|---|---|
| Mean | 0.87 |
| Median | 0.93 |
| On the 36 concordant paths | 0.90 |
| On the 12 divergent paths | 0.79 |
| Paths approved | 49 / 50 |

The badly classified whey protein scored 0.63. The concert ticket — a deliberately out-of-taxonomy input — landed on `Gift Cards` with 0.65 and was **approved**. The old judge rejected 14 out of 50; `path_score` rejects 1. The gap between concordant (0.90) and divergent (0.79) is real, but the distributions overlap: no threshold separates the two groups.

The reason is structural. `path_score` measures how *concentrated* the decision is, not whether it's *right*. A model can be confident and wrong, and that's exactly what happens when it picks a plausible but incorrect branch. Raising the threshold doesn't help — it would penalize deep paths, where a geometric mean falls by construction.

The fix, if those false positives matter, is a final verification question over the complete path: "does this path actually describe this product?" That's an independent judgment instead of a function of the same probabilities that produced the choice. It costs one request — roughly 0.43 s, +31% latency, a couple hundred tokens. Which is to say: you buy back a sliver of the agentic loop's self-correction, and you pay for it in exactly the currency you were trying to save.

## How I'd choose

Not "which is better." The two systems are good at different things, and the benchmark makes the boundary unusually legible.

**Reach for typed judgments (Jev, System One) when the workload is high-volume and latency and cost are hard constraints.** Structured decisions over a known space, most inputs unambiguous, a long tail you can afford to get wrong or route elsewhere. Here the agentic loop is paying 7x in time and 2x in calls for a capability most of your traffic never exercises.

**Keep the agentic loop where the cases are hard and being right matters more than being fast.** The loop's real product isn't tool calling — it's the ability to reconsider. When a first-level choice can only be evaluated in light of what shows up three levels down, a system that can backtrack will beat one that commits, every time.

The pragmatic answer is that these aren't two competing architectures, they're two layers of the same one. **Jev is a classification primitive; the agent is a reasoning loop. The loop should be allowed to call the primitive.**

Concretely, two ways to compose them, and they stack:

**Jev as a triage filter in front of the agent.** Every item enters the typed descent first. The easy majority — 36 out of 50 here, and in a real catalog the ratio is far more lopsided — comes out in 1.4 seconds and never touches an LLM. Only what fails triage gets promoted to the agentic loop, which can then afford its 10 seconds and its backtracking precisely because it's running on a small minority of traffic. You spend the expensive capability where it changes the answer, instead of paying for it on every ceramic mug in the catalog. The blocker is the routing signal, not the engines: `path_score` won't do it, for the structural reason above. A discriminative escalation criterion — a distribution flat across the top candidates, a final verification question, disagreement between two levels — is the actual engineering work.

**Jev as a tool the agent calls.** Instead of the agent walking the taxonomy by emitting text one level at a time, it gets `classify(description, node) -> distribution` as a tool and uses it as a subroutine. The agent keeps what it's uniquely good at — holding the whole problem in view, noticing three levels down that the branch makes no sense, backing out — and stops paying 1.3 s a turn to produce a category name a typed model returns in 0.43 s with calibrated probabilities attached. The loop gets cheaper per step, so it can afford *more* steps: more backtracking on the cases that need it, not less.

Both readings point the same way. The mistake isn't picking the wrong engine — it's assuming one engine has to do the whole job.

## What these numbers don't say

Worth being explicit, since it's easy to over-read a single run:

- The two runs didn't have the same concurrency conditions (5 threads vs sequential). The 7x is generous; the 3x per call is not.
- **Cost in euros is unknown.** Jev's pricing isn't published yet; the rates in `settings.py` are still OpenAI's, kept as a placeholder. Until the first invoice, the real delta could be larger or smaller than 36%.
- Quality was judged by one annotator with no ground truth. Twelve cases out of fifty is far too few for an error rate.
- One run per configuration. No measurement of day-to-day variance, which on a remote API is not negligible.
- No measurement under load. Everything sequential, one client at a time: behavior with concurrent requests and TypeSafe's rate limits are unknown.
