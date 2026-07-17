---
name: write-podcast-script
description: Use when converting an existing blog post in content/ into a single-voice podcast episode script (spoken-style monologue) written to podcast/<slug>.md.
---

# Write Podcast Script

## Overview

Converts an existing Pelican blog post into a **single-voice podcast script** — a
spoken-style monologue in the author's first-person voice, saved to
`podcast/<slug>.md`. The goal is text ready to read aloud (or feed to a TTS),
faithful to the whole post but rewritten for the ear.

Scope: one post at a time, full adaptation, script text only (no audio). Do NOT
edit the source post.

## When to Use

- "convert this post to a podcast" / "podcast script from content/foo.md"
- "make an episode from post X"
- Turning a written article into something meant to be spoken and listened to.

## Workflow

1. Get the post path (`content/<file>.md`). If not provided, ask for it.
2. Read the post. Derive the **slug** from its front matter:
   - YAML front matter (fenced with `---`): read the `slug:` key.
   - Classic Pelican (a `Slug:` line before the first blank line): read it.
   - If no slug field is present: derive it from the filename (drop `.md`).
3. Generate the monologue script following the style and structure rules below,
   covering **every** point of the post (full adaptation), in the post's order.
4. Write it to `podcast/<slug>.md`, creating the `podcast/` folder if absent.
   If `podcast/<slug>.md` already exists, ask before overwriting.

## Spoken-style rules

- First person, short sentences, oral transitions ("ora, la parte interessante è…").
- No visual references: never "as shown above", "in the table", "see the figure".
- Expand acronyms on first use: "MCP, il Model Context Protocol".
- Write numbers, symbols and percentages the way they are spoken.
- Optional `[pausa]` sparingly, for beats. No Markdown inside spoken lines.
- Write in the **same language as the source post** (do not translate).
- Match the author's voice from the source post — same stance and tone, just spoken.

## Handling code, tables, links, images

- **Code / commands:** explain what they DO, by meaning — never read the syntax.
  Say "in pratica gli passi il contenuto e la cartella di output", not
  `pelican content -o output`. Never read symbols, flags, or punctuation.
- **Tables / data:** summarize the point in words ("i margini scendono dal 90% al 60% circa").
- **Images / diagrams:** describe only the concept they illustrate.
- **Links:** "trovi il riferimento nelle note dell'episodio".

## Script structure

Start with a light metadata header, then the spoken content with service markers
on their own lines:

```
# Podcast — <post title>
Fonte: content/<slug>.md · Durata stimata: ~N min · Voce: singola

[COLD OPEN]
<2-3 sentence hook that grabs attention>

[INTRO]
<greeting + what this episode is about>

[CORPO]
<full spoken adaptation, in the post's order>

[OUTRO]
<wrap-up + invitation to read the post / subscribe>
```

The `[COLD OPEN]` / `[INTRO]` / `[CORPO]` / `[OUTRO]` markers are for the
author or TTS and stay on their own lines, separate from the spoken text.

## Self-check before writing the file

- Every section and argument of the post is represented, in the post's order.
- No visual references, and no read-aloud code or syntax slipped in.
- Acronyms expanded on first use; numbers and symbols spoken.
- The four markers are present, each on its own line.
- Output path is `podcast/<slug>.md`; the folder is created; an existing file was confirmed.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Reading code/commands verbatim | Explain their meaning only; never the syntax. |
| Leaving "as shown above / in the table" | Rewrite for the ear; no visual references. |
| Markdown (bold, inline code, bullet syntax) inside spoken lines | Plain spoken prose only. |
| Condensing or summarizing the post | Full adaptation — cover every point, in order. |
| Writing into content/ | Scripts go to `podcast/<slug>.md`, outside content/. |
| Overwriting an existing script silently | Ask before overwriting `podcast/<slug>.md`. |

## Example

Source post excerpt:

> ## What the article gets right
> First, value *is* migrating. If your product is a thin wrapper over a model
> call, your margin is a rounding error on someone else's capex.

Script excerpt:

```
[CORPO]
So let's start with where the article is right. Value really is migrating. And
here's the blunt version: if your product is just a thin shell around a single
model call, your margin is a rounding error on somebody else's infrastructure
bill.
```
