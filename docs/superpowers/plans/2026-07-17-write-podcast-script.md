# write-podcast-script Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Creare la skill `write-podcast-script` che converte un post del blog Pelican nello script di un podcast in stile parlato (monologo a voce singola), scritto in `podcast/<slug>.md`.

**Architecture:** È una skill di sole istruzioni (come `write-pelican-post`): un singolo file `.claude/skills/write-podcast-script/SKILL.md` con front matter YAML (`name`, `description`) + corpo di istruzioni. Nessun codice runtime. La validazione avviene facendo il dogfood della skill su un post reale e verificando l'output contro la checklist della skill stessa.

**Tech Stack:** Markdown + YAML front matter (convenzione Claude Code skills). Verifica con `python` (parsing YAML) e `grep`. Lavoro su branch `main`.

## Global Constraints

- Il file è un singolo `.claude/skills/write-podcast-script/SKILL.md` con front matter YAML (`name`, `description`).
- Formato dello script: monologo a voce singola, prima persona.
- Fedeltà: adattamento integrale (tutti i punti del post, nell'ordine del post).
- Codice e tecnica: spiegati **solo nel significato**, mai letti nella sintassi.
- Output: `podcast/<slug>.md` (cartella creata se assente; conferma prima di sovrascrivere). `podcast/` sta fuori da `content/`.
- Slug derivato dal front matter del post gestendo **entrambi** i formati del blog (YAML `---` e classico `Slug:`); fallback dal nome file.
- Marcatori di servizio `[COLD OPEN]` / `[INTRO]` / `[CORPO]` / `[OUTRO]`, ognuno su riga propria.
- Tutto su branch `main` (non nel worktree Substack).

## File Structure

- Create: `.claude/skills/write-podcast-script/SKILL.md` — l'intera skill (unica unità).
- Create (dogfood, Task 2): `podcast/<slug>.md` — primo script di esempio generato dalla skill.

---

### Task 1: Scrivere `SKILL.md`

**Files:**
- Create: `.claude/skills/write-podcast-script/SKILL.md`

**Interfaces:**
- Consumes: nulla.
- Produces: la skill `write-podcast-script`, invocabile come command, con front matter (`name: write-podcast-script`) e le sezioni: Overview, When to Use, Workflow, Spoken-style rules, Handling code/tables/links/images, Script structure, Self-check, Common Mistakes, Example.

- [ ] **Step 1: Creare la cartella e il file con questo contenuto esatto**

Creare `.claude/skills/write-podcast-script/SKILL.md` con:

````markdown
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
Allora, partiamo da dove l'articolo ha ragione. Il valore si sta davvero
spostando. E il punto è brutale: se il tuo prodotto è solo un guscio sottile
intorno a una chiamata a un modello, il tuo margine è un errore di
arrotondamento sulla spesa in infrastruttura di qualcun altro.
```
````

- [ ] **Step 2: Verificare che il front matter YAML sia valido**

Run:
```bash
python -c "d=open('.claude/skills/write-podcast-script/SKILL.md').read().split('---'); import yaml; m=yaml.safe_load(d[1]); assert m['name']=='write-podcast-script' and m.get('description'); print('front matter ok')"
```
Expected: stampa `front matter ok`

- [ ] **Step 3: Verificare che tutte le sezioni richieste siano presenti**

Run:
```bash
for h in "# Write Podcast Script" "## Overview" "## When to Use" "## Workflow" "## Spoken-style rules" "## Handling code, tables, links, images" "## Script structure" "## Self-check before writing the file" "## Common Mistakes" "## Example"; do grep -qF "$h" .claude/skills/write-podcast-script/SKILL.md && echo "OK  $h" || echo "MISSING  $h"; done
```
Expected: dieci righe tutte con prefisso `OK` (nessuna `MISSING`)

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/write-podcast-script/SKILL.md
git commit -m "feat: skill write-podcast-script (post -> script podcast monologo)"
```

---

### Task 2: Dogfood su un post reale e rifinire

**Files:**
- Create: `podcast/hardware-ate-software-survivors-become-agents.md`
- Modify (se il dogfood rivela lacune): `.claude/skills/write-podcast-script/SKILL.md`

**Interfaces:**
- Consumes: la skill di Task 1; il post `content/hardware-ate-software-survivors-become-agents.md` (post reale, formato front matter classico, con codice/link — buon banco di prova).
- Produces: `podcast/<slug>.md` conforme alle regole della skill.

- [ ] **Step 1: Applicare la skill al post di prova**

Seguendo `.claude/skills/write-podcast-script/SKILL.md`, leggere
`content/hardware-ate-software-survivors-become-agents.md`, derivarne lo slug
(`hardware-ate-software-survivors-become-agents`, dal campo `Slug:` classico) e
generare il monologo integrale in stile parlato. Scrivere il risultato in
`podcast/hardware-ate-software-survivors-become-agents.md`, con l'header di
metadati e i quattro marcatori di servizio.

- [ ] **Step 2: Verificare la struttura dell'output (marcatori + niente codice letto)**

Run:
```bash
f=podcast/hardware-ate-software-survivors-become-agents.md
for m in "[COLD OPEN]" "[INTRO]" "[CORPO]" "[OUTRO]"; do grep -qF "$m" "$f" && echo "OK  $m" || echo "MISSING  $m"; done
grep -nF '```' "$f" && echo "ATTENZIONE: blocchi di codice presenti (non dovrebbero esserci)" || echo "OK  nessun blocco di codice"
grep -niE "come (sopra|sotto)|nella tabella|come si vede|vedi (la )?figura" "$f" && echo "ATTENZIONE: riferimenti visivi" || echo "OK  nessun riferimento visivo"
```
Expected: i quattro marcatori `OK`; `OK  nessun blocco di codice`; `OK  nessun riferimento visivo`

- [ ] **Step 3: Auto-verifica contro la checklist della skill**

Rileggere l'output e confermare, punto per punto, la sezione "Self-check before
writing the file" della skill: tutti gli argomenti del post presenti e in
ordine; acronimi espansi alla prima occorrenza; codice spiegato solo nel
significato; nessun markdown dentro le battute. Se emergono lacune ricorrenti
(es. la skill non è chiara su qualcosa), correggere `SKILL.md` di conseguenza —
altrimenti lasciarlo invariato.

- [ ] **Step 4: Commit**

```bash
git add podcast/hardware-ate-software-survivors-become-agents.md
# includere anche SKILL.md solo se modificato allo Step 3:
git add .claude/skills/write-podcast-script/SKILL.md 2>/dev/null || true
git commit -m "test: primo script podcast di esempio (dogfood write-podcast-script)"
```

---

## Self-Review

**1. Spec coverage:**
- Skill di istruzioni, singolo SKILL.md → Task 1. ✓
- Monologo voce singola, prima persona → front matter + Spoken-style rules. ✓
- Adattamento integrale → Workflow step 3 + Common Mistakes ("Condensing"). ✓
- Codice spiegato solo nel significato → sezione Handling code. ✓
- Output `podcast/<slug>.md`, cartella creata, conferma sovrascrittura → Workflow step 4. ✓
- Slug da entrambi i formati front matter + fallback → Workflow step 2. ✓
- Marcatori di servizio su riga propria → Script structure + verifica Task 2 step 2. ✓
- Creazione su `main` → Global Constraints + questo piano vive su main. ✓
- Nessun test automatico, verifica via dogfood → Task 2. ✓

**2. Placeholder scan:** nessun "TBD/TODO". I `<...>` dentro il blocco Script structure sono segnaposto **interni al template dello script** (parte del contenuto della skill), non lacune del piano. Ogni step mostra contenuto o comando reale.

**3. Type consistency:** nomi coerenti ovunque — `write-podcast-script`, `podcast/<slug>.md`, i quattro marcatori, i titoli di sezione usati in Task 1 step 3 corrispondono a quelli scritti nel file in Task 1 step 1.

## Fuori scope (come da spec)

Generazione audio/TTS, formato a due voci, episodi condensati, conversione batch, modifica dei post esistenti.
