---
name: write-pelican-post
description: Use when creating or scaffolding a new blog post for this Pelican blog (Markdown files in content/, pelican-yaml-metadata plugin) — writing a new post, generating its front matter/metadata, or choosing its slug, tags, category, or SEO description.
---

# Write Pelican Post

## Overview

Scaffolds a **new** post for this Pelican blog with a single, consistent metadata
format and SEO-ready title/description. The blog's existing posts use two conflicting
metadata styles — this skill removes the ambiguity by fixing one canonical format.

Scope: new posts only. Do NOT normalize existing posts or rewrite prose style.

## When to Use

- "Write a new blog post about X" / "create a Pelican post" / "add a post to content/"
- Generating or fixing the front matter (metadata) of a new post
- Choosing the slug, tags, category, or meta description for a new post

## Canonical front matter (ALWAYS this exact shape)

Always use **YAML front matter** fenced with `---`. Never the classic
`Title:`/`Category:` Pelican style, even if some existing posts use it.

```yaml
---
title: "Post title in title case"
date: 2026-07-15 22:48
tags:
- AI
- LLM
category: blog
author: samreghenzi
description: "Meta description, ~150–160 characters, sells the post for search results."
slug: post-title-in-title-case
---
```

## Field rules (fixed — do not vary)

| Field | Rule |
|-------|------|
| `title` | Quoted string, engaging, title case. |
| `date` | **Current** local date-time, format `YYYY-MM-DD HH:MM`. |
| `tags` | YAML list, 3–6 items. See tag rules below. |
| `category` | **Always** `blog`. Never `AI` or any other value. |
| `author` | **Always** `samreghenzi` (never `Sam Reghenzi`). |
| `description` | Quoted, ~150–160 chars, SEO meta description. **One** space after the colon. |
| `slug` | **Always present**, kebab-case derived from the title. |

## Tag rules

- 3–6 tags, preferring the blog's existing vocabulary before inventing new ones.
- **Known acronyms UPPERCASE:** `AI`, `LLM`, `MCP`, `ML`, `GPU`, `RSS`.
- **Everything else lowercase:** `python`, `devops`, `terraform`, `security`, `oauth`,
  `claude`, `tokens`, `skills`, `llama`, `motorcycle`, `lifestyle`, `personal`.
- Product/model names that aren't acronyms are lowercase (`llama`, `ollama`, `vllm`).

Existing vocabulary: AI, LLM, MCP, ML, python, devops, terraform, secops,
dataengineering, security, oauth, claude, tokens, skills, motorcycle, lifestyle, personal.

## SEO

- `title`: specific and compelling; put the concrete subject early.
- `description`: ~150–160 characters, one sentence, states the payoff/benefit of reading.
  This is the search-result snippet — make it stand on its own.

## Workflow

1. Get the topic/title and the post body (provided or pasted by the user).
2. Derive the slug: lowercase the title, replace spaces/punctuation with hyphens.
3. Filename: `content/<slug>.md`.
4. Assemble the canonical front matter using the field/tag/SEO rules above, with the
   current date-time.
5. Write the file to `content/<slug>.md`.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Copying the classic `Title:`/`Category:` style from some existing posts | Always YAML front matter fenced with `---`. |
| `category: AI` (or any topic as category) | Category is always `blog`; express the topic via tags. |
| Capitalizing non-acronym tags (`Llama`, `Python`, `Devops`) | Only real acronyms uppercase; everything else lowercase. |
| Omitting `slug` | Slug is mandatory for stable URLs. |
| `author: Sam Reghenzi` | Always `samreghenzi`. |
| Double space after `description:` | Exactly one space. |

## Full Example

```markdown
---
title: "Running Llama 3 Locally with vLLM on a Budget GPU"
date: 2026-07-15 22:48
tags:
- AI
- LLM
- llama
- vllm
- GPU
category: blog
author: samreghenzi
description: "How to serve Llama 3 on a consumer-grade GPU with vLLM — quantization and memory tricks that keep throughput usable without a data-center budget."
slug: running-llama-3-locally-vllm-budget-gpu
---

You don't need an H100 to run a capable open-weight model at home...
```
