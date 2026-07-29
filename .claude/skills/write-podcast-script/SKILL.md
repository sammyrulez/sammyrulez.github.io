---
name: write-podcast-script
description: Use when converting an existing blog post in content/ into a single-voice podcast episode script (spoken-style monologue) ready for ElevenLabs v3, saved as one or more podcast/<slug>-NN.txt files.
---

# Write Podcast Script

## Overview

Converts an existing Pelican blog post into a **single-voice podcast script** — a
spoken-style monologue in the author's first-person voice, produced as **uno o più
file di testo puro pronti per ElevenLabs**, salvati in `podcast/<slug>-NN.txt`.
I file contengono solo testo parlato + tag `<break>` per le pause, senza Markdown né header.

Scope: one post at a time, full adaptation, script text only (no audio). Do NOT
edit the source post. Per generare l'audio dai file .txt prodotti, vedi la sezione
"Generazione audio (ElevenLabs)" più avanti — è un passo separato e opzionale.

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
- Pause brevi con `<break time="0.5s"/>`, pause fra momenti dell'episodio con `<break time="1.0s"/>`. No Markdown inside spoken lines.
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

Ogni file contiene SOLO testo parlato + tag `<break>` per le pause. Nessun header,
nessun titolo, nessuna riga "Fonte:", nessun Markdown, nessun marker di sezione
testuale. L'utente incolla il contenuto del file in ElevenLabs senza tagliare nulla.

L'episodio segue comunque l'arco cold open → intro → corpo → outro, ma:

- I confini fra i momenti dell'episodio (cold open → intro → corpo → outro) NON sono
  scritti come marker: si rendono con una pausa `<break time="1.0s"/>`.
- Le pause brevi (un beat dentro il discorso) si rendono con `<break time="0.5s"/>`.
- Nessun audio tag fra parentesi quadre: l'unico marker ammesso nel testo è `<break time="…"/>`.

## Regola di split

- Ogni file resta sotto ~3.000 caratteri.
- Taglia solo su confini naturali: fine frase o fine paragrafo, preferendo i
  confini fra i momenti dell'episodio (cold open → intro → corpo → outro).
- Non tagliare MAI dentro un tag `<break>`.
- Evita code minuscole: se l'ultimo pezzo risulterebbe sotto ~250 caratteri,
  accorpalo al precedente.
- Numera i file `-01`, `-02`, … Se l'episodio sta sotto il limite, produci
  comunque un solo `podcast/<slug>-01.txt`.

## Self-check before writing the file

- Ogni sezione e argomento del post è rappresentato, nell'ordine del post.
- Nessun riferimento visivo e nessun codice/sintassi letto alla lettera.
- Acronimi espansi al primo uso; numeri e simboli scritti come si pronunciano.
- File 100% puliti: nessun header, nessun Markdown, nessun marker di sezione testuale.
- Nessun audio tag fra parentesi quadre; le pause sono solo `<break time="…"/>`.
- Ogni file < ~3.000 caratteri, tagliato su confini naturali, mai dentro un tag,
  niente code sotto ~250 caratteri.
- Output in `podcast/<slug>-NN.txt`; cartella creata; file esistenti confermati.

## Generazione audio (ElevenLabs)

Passo SEPARATO e SOLO su richiesta esplicita ("genera anche l'audio"). La normale
generazione dei .txt NON chiama mai l'API e non consuma crediti.

Prerequisiti:
- I file `podcast/<slug>-NN.txt` devono esistere già (generali prima con questa skill).
- Variabili d'ambiente impostate: `ELEVENLABS_API_KEY` e `ELEVENLABS_VOICE_ID`.
  Se mancano, chiedile all'utente; non stamparle né scriverle su file.
- Dipendenza installata nel venv:
  `venv/bin/pip install -r .claude/skills/write-podcast-script/requirements-audio.txt`

Comando:
  `venv/bin/python .claude/skills/write-podcast-script/generate_audio.py <slug>`
  Opzioni: `--podcast-dir DIR` (default `podcast`), `--force` (sovrascrive i .mp3).

Output: un file `podcast/<slug>-NN.mp3` per ogni chunk (`eleven_multilingual_v2`,
`mp3_44100_128`). Chiamare l'API consuma crediti: di default i .mp3 già presenti
vengono saltati (usa `--force` per rigenerarli).

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Reading code/commands verbatim | Explain their meaning only; never the syntax. |
| Leaving "as shown above / in the table" | Rewrite for the ear; no visual references. |
| Usare audio tag fra parentesi quadre (es. `[thoughtful]`, `[pause]`) | Nessun audio tag; le pause sono solo `<break time="…"/>`. |
| Markdown o marker di sezione nel file .txt | Solo testo parlato + `<break>`; niente header/Markdown/marker. |
| Un unico file oltre ~3.000 caratteri | Spezza in `podcast/<slug>-NN.txt` su confini naturali. |
| Writing into content/ | Scripts go to `podcast/<slug>-NN.txt`, outside content/. |

## Example

Source post excerpt:

> ## What the article gets right
> First, value *is* migrating. If your product is a thin wrapper over a model
> call, your margin is a rounding error on someone else's capex.

Script excerpt (file `podcast/<slug>-01.txt`):

```
So let's start with where the article is right. Value really is migrating. And here's
the blunt version: if your product is just a thin shell around a single model call, your
margin is a rounding error on somebody else's infrastructure bill. <break time="1.0s"/>
```
