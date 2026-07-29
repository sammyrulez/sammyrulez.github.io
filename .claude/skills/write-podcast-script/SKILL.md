---
name: write-podcast-script
description: Use when converting an existing blog post in content/ into a single-voice podcast episode script (spoken-style monologue) ready for ElevenLabs, saved as one or more podcast/<slug>-NN.txt files, with optional on-demand audio generation via the ElevenLabs API.
---

# Write Podcast Script

## Overview

Converts an existing Pelican blog post into a **single-voice podcast script** — a
spoken-style monologue in the author's first-person voice, produced as **uno o più
file di testo puro pronti per ElevenLabs**, salvati in `podcast/<slug>-NN.txt`.
I file contengono solo testo parlato + tag `<break>` per le pause, senza Markdown né header.

Scope: one post at a time, full adaptation. Il passo base produce solo i file .txt;
la generazione audio è un passo separato e opzionale (vedi "Generazione audio
(ElevenLabs)" più avanti). Do NOT edit the source post.

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
   - Genera inoltre `podcast/<slug>-intro.txt`: un teaser breve (2–4 frasi) con saluto +
     hook accattivante sull'argomento dell'episodio. Il saluto e l'introduzione stanno SOLO
     qui: i chunk `-NN.txt` NON aprono più con cold open/saluto/intro — il `-01` inizia
     direttamente dal corpo.

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

Il cold open, il saluto e l'introduzione dell'argomento vivono esclusivamente in
`podcast/<slug>-intro.txt` (vedi sezione "Intro (teaser)"). I chunk `-NN.txt` coprono
corpo → outro: il `-01` inizia direttamente dal corpo, senza ripetere saluto o intro.

- I confini fra i momenti del corpo (es. transizione verso l'outro) si rendono con una
  pausa `<break time="1.0s"/>`.
- Le pause brevi (un beat dentro il discorso) si rendono con `<break time="0.5s"/>`.
- Nessun audio tag fra parentesi quadre: l'unico marker ammesso nel testo è `<break time="…"/>`.

## Intro (teaser)

`podcast/<slug>-intro.txt` è un teaser di 2–4 frasi: saluto + un hook che incuriosisce
sull'argomento (tono da trailer). Stesse regole degli altri file: prima persona, stile
parlato, nessun audio tag fra parentesi quadre, `<break time="…"/>` ammesso, nessun
riferimento visivo, nessun Markdown/header, stessa lingua del post. È testo puro pronto
per la TTS.

## Regola di split

- Ogni file resta sotto 40000 caratteri (limite vincolante: 1 credito ElevenLabs ≈ 1 carattere).
- Di norma l'episodio sta in UN solo `podcast/<slug>-01.txt`; si splitta in `-02`, `-03`, …
  solo se il testo supererebbe 40000 caratteri.
- Quando serve tagliare: solo su confini naturali (fine frase o paragrafo), mai dentro un
  `<break>`. Evita code sotto ~250 caratteri.

## Self-check before writing the file

- Ogni sezione e argomento del post è rappresentato, nell'ordine del post.
- Nessun riferimento visivo e nessun codice/sintassi letto alla lettera.
- Acronimi espansi al primo uso; numeri e simboli scritti come si pronunciano.
- File 100% puliti: nessun header, nessun Markdown, nessun marker di sezione testuale.
- Nessun audio tag fra parentesi quadre; le pause sono solo `<break time="…"/>`.
- Vincolante: ogni file (intro e ogni chunk) è < 40000 caratteri.
- Output in `podcast/<slug>-NN.txt`; cartella creata; file esistenti confermati.
- Esiste `podcast/<slug>-intro.txt` (teaser 2–4 frasi: saluto + hook).
- Il chunk `-01` NON ripete saluto/cold open/intro: inizia dal corpo.

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
`mp3_44100_128`). Viene generato anche `podcast/<slug>-intro.mp3` (l'intro è sintetizzata per prima).

Chiamare l'API consuma crediti: di default i .mp3 già presenti
vengono saltati (usa `--force` per rigenerarli).

Retry automatico su crediti esauriti (opzionale):
  `venv/bin/python .claude/skills/write-podcast-script/generate_audio.py <slug> --wait`
  Con `--wait`, se la quota è esaurita lo script legge la data di reset e attende, poi
  riprende (idempotente). Opzioni: `--max-cycles N` (default 4), `--max-wait-seconds S`
  (default ~32 giorni). Interrompibile con Ctrl-C.
  Nota: `--wait` richiede una chiave ElevenLabs con permesso `user_read` (per leggere la
  data di reset); senza, lo script esce spiegando cosa manca.
Lo script rifiuta file oltre 40000 caratteri senza chiamare l'API.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Reading code/commands verbatim | Explain their meaning only; never the syntax. |
| Leaving "as shown above / in the table" | Rewrite for the ear; no visual references. |
| Usare audio tag fra parentesi quadre (es. `[thoughtful]`, `[pause]`) | Nessun audio tag; le pause sono solo `<break time="…"/>`. |
| Markdown o marker di sezione nel file .txt | Solo testo parlato + `<break>`; niente header/Markdown/marker. |
| Un file oltre 40000 caratteri | Spezza in `podcast/<slug>-NN.txt`; nessun file supera 40000. |
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
