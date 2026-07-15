Title: Hardware Ate Software. But the Survivors Become Agents
Date: 2026-07-14 09:30
Category: AI
Tags: llm, agents, hardware, inference, mcp, economics, stack
Slug: hardware-ate-software-survivors-become-agents
Author: Sam Reghenzi
Summary: A response to "Software Ate the World, Now Hardware Is Eating Software." The diagnosis is right — value is migrating and point software is being crushed. The prognosis is wrong. When the bottom of the stack commoditizes, value doesn't stay there. It climbs back up to the layer the thesis forgot: the agent.

There's a piece going around called [*Software Ate the World. Now Hardware Is Eating Software*](https://www.datagravity.dev/p/software-ate-the-world-now-hardware), and it is good enough that I want to argue with it. The thesis is that the center of economic gravity in tech is sliding *down* the stack — toward the layers with the deepest physical constraints and the strongest control points: semiconductors, data platforms, and the inference engines that run open models. NVIDIA at ~75% gross margins. Hyperscaler capex heading toward $5.3 trillion by 2030. Application margins compressing from the 75-90% of the SaaS era down to 50-60%. The conclusion: stop betting on apps, start betting on silicon and data gravity.

Part of what makes the argument land is that the *kind* of hardware underneath us has changed. For twenty years the substrate was commodity: RAM, CPU, disk — parts that were cheap, interchangeable, and evolving slowly enough that nobody thought about them. You provisioned them and forgot them. The AI stack runs on GPUs, and GPUs are a different animal entirely: faster-moving on the evolutionary curve, far more expensive, and carrying a margin the commodity components never did. When the foundation stops being fungible and starts being a scarce, high-margin, fast-obsolescing asset, it's natural to conclude that this is where the money now lives. That shift is real, and it's the strongest part of the article.

I agree with almost every number. I disagree with where the arrow points.

## What the article gets right

Let me not build a strawman. The diagnosis is correct in two important ways.

First, value *is* migrating. The comfortable two-decade assumption that the application layer is where money accretes is genuinely breaking. If your product is a thin wrapper over a model call, your margin is a rounding error on someone else's capex.

Second — and this is the part people flinch at — **point software is condemned.** The single-purpose tool, the app that does one thing behind a form and a database, is being squeezed exactly as the article says. That compression from 90% to 50% margins is real, and it isn't a blip. So far, so aligned.

Where I get off the train is the prognosis. The article measures where the *capital* is going and assumes that's where the *value* will be captured. Those are not the same thing.

## Capital intensity is not value capture

The whole argument rests on a slide from "this layer is expensive and physically constrained" to "this layer captures the value." But capital intensity and value capture are different axes. Railroads were brutally capital-intensive; most of the durable value ended up with the businesses that *ran on top of the rails*, not the ones that laid them. Being hard to build is not the same as being where the margin lives.

Here's the move the article misses: **commoditization at the bottom doesn't destroy value, it relocates it.** When a layer gets cheap and abundant, the barrier drops and value floods into whatever sits on top and can now do something new.

I keep bumping into this in practice, not in theory. A few months ago I [ran Gemma 4 31B on a 32GB Apple Silicon Mac with Ollama](/running-gemma-4-31b-on-an-apple-silicon-mac-with-ollama.html). No tokens, no API bill, no hyperscaler in the loop. The article would file that under "inference commoditizing, margins compressing." Fine. But look at what commodity inference actually *did*: it put a capable model on my desk and collapsed the cost of building something on top of it to roughly zero. That is not value destruction. That is the barrier falling — and value doesn't evaporate when a barrier falls, it moves to whoever is standing on the other side of it.

The open-vs-closed gap closing from 8% to 1.7% in a year is the same story told as a threat. The article reads it as "models are commoditizing, so the value sinks to whoever owns the compute." I read it as "the intelligence layer just became a utility, so the interesting question is what you *build* with a utility."

## The layer the thesis forgot

The article has five layers: semiconductors, open models and inference, premium models, data platforms, applications. Notice what's missing. There is no layer for the thing that turns a commodity model into something that does work in the world. No orchestration. No integration. No agent.

That omission is the whole disagreement in one gap.

Because the honest thing to say about point software is not that it's dying — it's that it's *metamorphosing*. The app stops being a static interface you operate and becomes an agent that operates on your behalf. Features stop being screens and become capabilities the agent can reach for. The value was never in the form and the database; it was in the judgment about what to do next, and that judgment is exactly what an agent embodies.

This is not a slide deck abstraction for me. It's most of what I've been writing about. The reason I keep picking at [MCP versus skills](/skills-vs-mcp-tokens-security.html), or at [the way OAuth cracks when you hand it to a model with no eyes and no hesitation](/oauth-original-sin-mcp-auth.html), is that this is the scaffolding of the agent layer. How a model reaches the outside world, what it's allowed to touch, how it holds a session — those aren't plumbing details below the value. In an agent-shaped world they *are* the value.

## Where gravity actually climbs

So if the bottom of the stack is commoditizing — and it is — where does the gravity go?

Not the GPUs. You can rent those by the hour, and the whole thrust of open models and local inference is to make the raw intelligence a fungible input. Owning silicon is owning the railroad.

The new control points are further up:

- **Orchestration** — the logic that decides which capability to invoke, in what order, and how to recover when a step fails. This is genuinely hard and genuinely defensible, and it lives nowhere in the five-layer map.
- **Proprietary data loops** — the article actually gets this half-right under "data gravity," but frames it as a moat for *platforms* rather than the fuel that makes an *agent* good at your specific problem.
- **Agent reliability and safety** — the boring, unglamorous work of making an autonomous thing trustworthy enough to hand real permissions. Whoever solves this owns a lock-in that no amount of capex buys.

None of these are cheap in capital. They're expensive in judgment, in data, and in the accumulated scar tissue of making agents behave. That's a different kind of moat than a fab, and it accrues to a different kind of builder.

## The engineer's version of the thesis

The article is written for an investor: it's a map of where to allocate *capital* across a stack. Read it as an engineer and the question changes — not "where do I put my money" but "where do I put my effort." And once you flip that lens, almost every conclusion inverts with it.

If you believe — as I do, and as [the argument that software becomes agents rather than standalone tools](https://www.youtube.com/watch?v=83fWzQSWB10) lays out — that every app worth keeping is going to become an agent, then the commoditization of hardware and inference isn't the headline. It's the *precondition*. Cheap, abundant, ownable intelligence is the raw material. The investor sees a low-margin commodity and walks away. The engineer sees a free input and asks what can finally be built now that it costs nothing. Those are opposite reactions to the same fact, and only one of them ships anything.

So let me be concrete about what building in an agent-shaped world actually looks like, because "software becomes agents" is easy to say and easy to get wrong.

### The interface inverts

The oldest assumption in application software is that a human drives and the software responds. You click, it reacts. Every screen, every form, every menu is scaffolding for a person operating a machine. The agent inverts this: the software drives, and the human sets intent and supervises. That is not a UI refresh — it's a different center of gravity for the whole system. The screen stops being the product. The product is the loop of *perceive → decide → act → check*, and the screen is just one place a human can peek into it.

Practically, this means the work you used to pour into the front end — the state management, the wizard flows, the careful choreography of what the user can click next — largely evaporates or moves. What replaces it is the design of the agent's **capability surface**: the set of actions it can take, described well enough that a model can choose between them correctly, with the guardrails that keep a wrong choice from being catastrophic. That is engineering work, and it's harder than the front end it replaces, because your "user" now has no eyes, no common sense, and no hesitation.

### Features stop being screens and become tools

In the old model, a feature is something you build *and then teach a human to find*: a button, a settings page, a documented workflow. In the agent model, a feature is a **tool the agent can reach for** — and the entire discipline of exposing tools to a model is exactly the terrain I keep writing about. Whether you reach for [MCP or a plain CLI skill](/skills-vs-mcp-tokens-security.html) is not a plumbing decision underneath the value. It *is* the product surface. Get the tool descriptions wrong and the smartest model in the world invokes the wrong capability at the wrong time. Get the permission boundaries wrong and you've handed [an OAuth token to something with no judgment about when to use it](/oauth-original-sin-mcp-auth.html).

This is where the article's five-layer map fails an engineer most concretely. There is no line item for "the contract between the agent and the world," and yet that contract is where most of the real engineering — and most of the real defensibility — now lives.

### What you actually invest in

If effort is the currency, here is where I'd spend it, in order:

- **The capability layer.** The tools, their descriptions, their boundaries, their failure modes. This is the new API design, and it's the highest-leverage code you'll write.
- **The data loop.** Not "data" as a static asset the way the article frames data gravity, but the *loop*: the agent acts, the outcome is captured, and that outcome makes the next action better. An agent with a tight loop on your specific problem beats a bigger model with none. This is a moat you build, not one you buy.
- **Reliability and evals.** The unglamorous scaffolding that tells you whether the agent is getting better or quietly regressing. In an agent-shaped product, your test suite is a behavioral one, and building it is most of the job.
- **Model-agnosticism.** Precisely *because* the intelligence layer is commoditizing, you should treat the model as a swappable part. The day I [ran Gemma on a Mac](/running-gemma-4-31b-on-an-apple-silicon-mac-with-ollama.html) I wasn't proving a Mac can host a model — I was proving the model is a component I can source three different ways. Build so that swapping it is a config change, not a rewrite, and the commoditization the article mourns becomes leverage you own.

Notice what's *not* on that list: owning the silicon, training a frontier model, betting the company on a fab. Those are capital plays, and they belong to people with capital. The engineer's plays are all further up — and they compound with judgment and data, which is the one kind of moat that gets *deeper* the cheaper the hardware underneath it gets.

### The product is the job

Everything above is about *how* you build. But the sharpest way to feel the shift is to look at *what you sell*. SaaS sells software: a tool your customer's team logs into and operates. Agent SaaS sells **work**: you take a job the customer's team currently does, you package it whole, and you sell the outcome as a service. The team stops operating a tool and starts handing off a responsibility.

It sounds like a small rewording. It changes everything about how both sides think. The buyer stops evaluating features and seat counts and starts asking a much simpler question — "will this reliably get the job done?" — the same question they'd ask when hiring. And the builder stops shipping capabilities and hoping the customer assembles them into value; you're now on the hook for the value itself. That's a heavier promise, and it's exactly why the margin follows it back up the stack. Nobody pays SaaS-commodity prices for something that shows up, does the work, and is accountable for the result.

This is also why the commoditization the article mourns is a tailwind here, not a threat. When the intelligence underneath is cheap and abundant, the cost of *doing the job* collapses — and the price you can charge is anchored to the human labor you're replacing, not to your compute bill. The gap between those two numbers is the whole business.

### What this looks like in the wild

The pattern is already shipping, and the tell is that these products don't describe themselves as software at all — they describe themselves as a role.

[Slang AI](https://www.slang.ai/) sells an "AI super host" for restaurants. It answers the phone, manages reservations, routes VIPs to a human, and pings staff when something needs attention. Nobody at the restaurant logs into a dashboard to "use the reservation feature" — the phone just gets answered, all of it, every time. The product *is* the host.

[Same Day](https://www.sameday.ai/) does the equivalent for home services: AI dispatchers and receptionists that answer calls, book jobs, and reschedule without a human touching them. Again, the sale isn't a tool — it's the front desk.

What makes both work is the bar they clear: handle one genuinely annoying job **better than a junior hire, faster than an agency, and cheaper than new headcount**. That's the whole value proposition, and notice it's measured against *people*, not against other software. That's the giveaway that these aren't apps anymore. You don't benchmark a SaaS tool against a receptionist. You benchmark an agent against one — because it's doing the receptionist's job.

### The prognosis, flipped

So yes: software ate the world, and now hardware is eating software. But something always crawls out of the thing that got eaten. This time it's the agent — and it's standing on all that cheap silicon, *using* it, not being replaced by it. The article looked down the stack and saw where the capital sinks. Look up the stack and you see where the work goes, and the work is where builders have always eventually captured the value.

The point software is dying. Long live the agent.
