# Design: generazione audio ElevenLabs per `write-podcast-script`

Data: 2026-07-28

## Contesto

La skill `write-podcast-script` converte un post del blog in un monologo parlato,
salvato come uno o più file `podcast/<slug>-NN.txt` pronti per la sintesi vocale.
Nella versione precedente questi file contenevano audio tag del modello ElevenLabs v3
(`[thoughtful]`, `[pause]`, …) e una palette chiusa di tag.

Nuova richiesta: la skill deve, **su richiesta**, generare i file audio dai `.txt` usando
le API di ElevenLabs. Poiché la generazione userà il modello stabile
`eleven_multilingual_v2` — che **non** interpreta gli audio tag v3 — questi tag non
hanno più utilità e vengono **eliminati del tutto** dall'output della skill.

## Decisioni prese

1. **Modello TTS:** `eleven_multilingual_v2` (stabile, sempre disponibile via API).
2. **Audio tag v3:** rimossi completamente dall'output della skill.
3. **Trigger audio:** passo separato, solo su richiesta esplicita dell'utente. La
   generazione dei `.txt` non chiama mai l'API.
4. **Output audio:** un file `.mp3` per ogni chunk `.txt` (nessuna concatenazione).
5. **Implementazione:** SDK Python `elevenlabs`, in un file di dipendenze separato.
6. **Configurazione:** da variabili d'ambiente (`ELEVENLABS_API_KEY`,
   `ELEVENLABS_VOICE_ID`).

## Parte A — La skill non produce più audio tag v3

### Cosa cambia in `SKILL.md`

- Rimuovere la sezione `## Audio tag v3` e la palette chiusa.
- I `.txt` contengono **solo testo parlato + tag di pausa `<break>`**.
- Le pause si rendono tutte con `<break time="…"/>` (supportato da
  `eleven_multilingual_v2`):
  - beat breve (ex `[pause]`): `<break time="0.5s"/>`
  - confine fra i momenti dell'episodio (cold open → intro → corpo → outro):
    `<break time="1.0s"/>`
- Aggiornare il self-check: nessun audio tag `[...]`; l'unico marker ammesso nel testo è
  `<break time="…"/>`.
- Aggiornare la tabella Common Mistakes: rimuovere le righe sulla palette/tag; aggiungere
  che non vanno usati audio tag fra parentesi quadre (solo `<break>` per le pause).
- L'arco cold open → intro → corpo → outro resta, reso con pause `<break>` e ritmo del
  testo, senza marker testuali (invariato rispetto a prima).

### Regole invariate

Restano tutte le regole "per l'orecchio": prima persona, niente riferimenti visivi,
acronimi espansi al primo uso, numeri/simboli scritti come si pronunciano, niente
Markdown, stessa lingua del post, adattamento completo e in ordine, codice spiegato per
significato, link → "in the show notes". Restano invariate anche la regola di split
(file < ~3.000 caratteri, confini naturali, mai dentro un `<break>`, niente code sotto
~250 caratteri) e il percorso `podcast/<slug>-NN.txt`.

### Rigenerazione dell'esempio

Rigenerare `podcast/hardware-ate-software-survivors-become-agents-*.txt` rimuovendo tutti
gli audio tag (`[thoughtful]`, `[serious]`, `[curious]`, `[excited]`) e convertendo ogni
`[pause]` in `<break time="0.5s"/>`. Il testo parlato non cambia; cambiano solo i marker.

## Parte B — Generazione audio ElevenLabs

### Script helper

- File committato, bundlato con la skill: `.claude/skills/write-podcast-script/generate_audio.py`.
- Firma d'uso: `python generate_audio.py <slug> [--podcast-dir DIR] [--force]`.
  - `<slug>`: identifica i file `podcast/<slug>-*.txt`.
  - `--podcast-dir`: cartella dei file (default `podcast/`).
  - `--force`: sovrascrive i `.mp3` esistenti senza chiedere (in assenza, salta i file
    già presenti e lo segnala).
- Comportamento:
  1. Legge `ELEVENLABS_API_KEY` e `ELEVENLABS_VOICE_ID` dall'ambiente. Se una manca:
     stampa un messaggio che dice quale impostare ed esce con codice non-zero, senza
     chiamare l'API.
  2. Trova i file `<podcast-dir>/<slug>-*.txt` ordinati per numero. Se non ce ne sono:
     messaggio ed exit non-zero.
  3. Per ogni `.txt`: se il `.mp3` corrispondente esiste e non c'è `--force`, salta e lo
     segnala; altrimenti legge il testo, chiama l'SDK `elevenlabs`
     (`model_id="eleven_multilingual_v2"`, `output_format="mp3_44100_128"`,
     `voice_id` dall'ambiente) e scrive `<podcast-dir>/<slug>-NN.mp3`.
  4. Riporta a fine esecuzione quali file sono stati generati e quali saltati.
- **Nessun preprocessing** del testo: i `.txt` sono già puliti (solo parlato + `<break>`),
  che è esattamente ciò che v2 accetta.
- Gestione errori di rete: se l'SDK solleva un errore (401/429/altro), lo script lo
  riporta e termina con codice non-zero, senza cancellare i `.mp3` già scritti in questa
  esecuzione.

### Struttura interna testabile

Separare la logica pura dalla rete, così la prima è testabile senza chiamare l'API:

- `discover_chunks(podcast_dir, slug) -> list[Path]` — trova e ordina i `.txt` per numero.
- `chunk_to_mp3_path(txt_path) -> Path` — mappa `<slug>-NN.txt` → `<slug>-NN.mp3`.
- `load_config(env) -> (api_key, voice_id)` — legge le env, solleva un errore chiaro se
  mancano.
- `synthesize(client, text, voice_id) -> bytes` — unica funzione che tocca la rete
  (l'SDK); il resto del programma non chiama l'API.
- `main()` — orchestrazione + CLI + I/O file.

### Dipendenza

- File separato `.claude/skills/write-podcast-script/requirements-audio.txt` con la sola
  riga `elevenlabs` (o versione pinnata a scelta dell'implementatore in base all'ultima
  stabile). **Non** va aggiunto a `requirements.txt` del blog, per non farlo installare
  dalla CI Pelican a ogni build.
- La skill istruisce a installarlo on demand nel venv:
  `venv/bin/pip install -r .claude/skills/write-podcast-script/requirements-audio.txt`.

### Documentazione nella skill

Nuova sezione in `SKILL.md`, es. `## Generazione audio (ElevenLabs)`, che descrive:
- che è un passo **separato e su richiesta** ("genera anche l'audio");
- i prerequisiti: env `ELEVENLABS_API_KEY` e `ELEVENLABS_VOICE_ID`, e l'install della
  dipendenza;
- il comando da eseguire;
- che l'output è `podcast/<slug>-NN.mp3`, uno per chunk;
- che chiamare l'API consuma crediti;
- la gestione dei file esistenti (`--force`) e il prerequisito che i `.txt` esistano.

## Testing

- `pytest` sulle funzioni pure: `discover_chunks` (ordinamento e filtro corretti),
  `chunk_to_mp3_path` (mappatura corretta), `load_config` (errore se env mancanti).
- La chiamata di rete (`synthesize` / `main` end-to-end) non è coperta da test automatici;
  va verificata manualmente con una chiave reale.
- Il test file vive accanto allo script:
  `.claude/skills/write-podcast-script/test_generate_audio.py`.

## Sicurezza

- La chiave API e il voice id arrivano solo da variabili d'ambiente; non vengono mai
  scritti su file, stampati nei log, o committati.

## Fuori scope

- Concatenazione dei chunk in un unico mp3 dell'episodio.
- Retry automatici, backoff, caching delle richieste.
- Upload dell'audio su servizi esterni.
- Scelta della voce diversa da quella in `ELEVENLABS_VOICE_ID`.
