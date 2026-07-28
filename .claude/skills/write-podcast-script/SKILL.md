---
name: write-podcast-script
description: Use when converting an existing blog post in content/ into a single-voice podcast episode script (spoken-style monologue) ready for ElevenLabs v3, saved as one or more podcast/<slug>-NN.txt files.
---

# Write Podcast Script

## Overview

Converts an existing Pelican blog post into a **single-voice podcast script** — a
spoken-style monologue in the author's first-person voice, produced as **uno o più
file di testo puro pronti per ElevenLabs v3**, salvati in `podcast/<slug>-NN.txt`.
I file contengono solo testo parlato + audio tag v3, senza Markdown né header.

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
4. Scrivi l'output come uno o più file `podcast/<slug>-NN.txt` (NN a due cifre,
   da 01), creando la cartella `podcast/` se assente. Applica la regola di split
   descritta sotto. Se esistono già file `podcast/<slug>-*.txt`, chiedi conferma
   prima di rigenerarli/sovrascriverli.

## Spoken-style rules

- First person, short sentences, oral transitions ("ora, la parte interessante è…").
- No visual references: never "as shown above", "in the table", "see the figure".
- Expand acronyms on first use: "MCP, il Model Context Protocol".
- Write numbers, symbols and percentages the way they are spoken.
- Pause brevi con `[pause]`, pause fra momenti dell'episodio con `<break time="1.0s"/>`. No Markdown inside spoken lines.
- Write in the **same language as the source post** (do not translate).
- Match the author's voice from the source post — same stance and tone, just spoken.

## Handling code, tables, links, images

- **Code / commands:** explain what they DO, by meaning — never read the syntax.
  Say "in pratica gli passi il contenuto e la cartella di output", not
  `pelican content -o output`. Never read symbols, flags, or punctuation.
- **Tables / data:** summarize the point in words ("i margini scendono dal 90% al 60% circa").
- **Images / diagrams:** describe only the concept they illustrate.
- **Links:** "trovi il riferimento nelle note dell'episodio".

## Struttura dell'output

Ogni file contiene SOLO testo parlato + audio tag v3 + tag di pausa. Nessun header,
nessun titolo, nessuna riga "Fonte:", nessun Markdown, nessun marker di sezione
testuale. L'utente incolla il contenuto del file in ElevenLabs senza tagliare nulla.

L'episodio segue comunque l'arco cold open → intro → corpo → outro, ma i confini fra
questi momenti NON sono scritti come marker: sono resi con una pausa più marcata
(`<break time="1.0s"/>`) e, dove serve, un cambio di tono via audio tag.

## Audio tag v3

Le parentesi quadre in ElevenLabs v3 sono audio tag. Usali così:

- Pause brevi: usa `[pause]` (mai `[pausa]`).
- Pause fra i momenti dell'episodio: `<break time="1.0s"/>`.
- Espressività: usa i tag con parsimonia, solo quando cambia genuinamente
  l'intenzione di una frase — mai su ogni frase.
- Palette CHIUSA consentita (non inventare altri tag: quelli fuori vocabolario
  vengono ignorati o pronunciati):
  [pause], [thoughtful], [curious], [serious], [excited], [laughs], [sighs],
  [sarcastic], [whispers].
- Gli audio tag sono in INGLESE anche se il parlato è in un'altra lingua: è così
  che ElevenLabs li riconosce. Il testo parlato resta nella lingua del post.

## Regola di split

- Ogni file resta sotto ~3.000 caratteri.
- Taglia solo su confini naturali: fine frase o fine paragrafo, preferendo i
  confini fra i momenti dell'episodio (cold open → intro → corpo → outro).
- Non tagliare MAI dentro un audio tag o un tag `<break>`.
- Evita code minuscole: se l'ultimo pezzo risulterebbe sotto ~250 caratteri,
  accorpalo al precedente.
- Numera i file `-01`, `-02`, … Se l'episodio sta sotto il limite, produci
  comunque un solo `podcast/<slug>-01.txt`.

## Self-check before writing the file

- Ogni sezione e argomento del post è rappresentato, nell'ordine del post.
- Nessun riferimento visivo e nessun codice/sintassi letto alla lettera.
- Acronimi espansi al primo uso; numeri e simboli scritti come si pronunciano.
- File 100% puliti: nessun header, nessun Markdown, nessun marker di sezione testuale.
- Solo audio tag della palette consentita; pause come `[pause]` / `<break>`.
- Ogni file < ~3.000 caratteri, tagliato su confini naturali, mai dentro un tag,
  niente code sotto ~250 caratteri.
- Output in `podcast/<slug>-NN.txt`; cartella creata; file esistenti confermati.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Reading code/commands verbatim | Explain their meaning only; never the syntax. |
| Leaving "as shown above / in the table" | Rewrite for the ear; no visual references. |
| Markdown o marker di sezione nel file .txt | Solo testo parlato + audio tag v3; niente header/Markdown. |
| Usare `[pausa]` o marker `[CORPO]/[INTRO]` | Pause con `[pause]`/`<break>`; niente marker di sezione. |
| Inventare audio tag fuori palette | Usa solo la palette v3 consentita. |
| Un unico file oltre ~3.000 caratteri | Spezza in `podcast/<slug>-NN.txt` su confini naturali. |
| Writing into content/ | Scripts go to `podcast/<slug>-NN.txt`, outside content/. |

## Example

Source post excerpt:

> ## What the article gets right
> First, value *is* migrating. If your product is a thin wrapper over a model
> call, your margin is a rounding error on someone else's capex.

Script excerpt (file `podcast/<slug>-01.txt`):

```
[thoughtful] So let's start with where the article is right. Value really is
migrating. And here's the blunt version: if your product is just a thin shell
around a single model call, your margin is a rounding error on somebody else's
infrastructure bill. <break time="1.0s"/>
```
