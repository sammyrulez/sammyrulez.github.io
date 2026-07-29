# Design: file intro (teaser) per episodio podcast

Data: 2026-07-29

## Contesto

La skill `write-podcast-script` converte un post in un monologo parlato, salvato come
file `podcast/<slug>-NN.txt`, e (su richiesta) genera i `.mp3` via
`generate_audio.py`. Oggi ogni episodio si apre con un cold open + saluto + intro
dell'argomento embeddati nel primo chunk.

Nuova richiesta: produrre, per ogni episodio, un **file intro separato** con saluto e
breve introduzione dell'argomento, e generarne anche l'audio.

## Decisioni prese

1. L'intro è un **file separato**: `podcast/<slug>-intro.txt`.
2. Saluto e introduzione si **spostano interamente** nell'intro: i chunk `-NN.txt` non
   ripetono saluto/cold open; il `-01` inizia direttamente dal corpo.
3. Stile intro: **teaser accattivante**, 2–4 frasi (saluto + hook sull'argomento).
4. `generate_audio.py` produce anche `podcast/<slug>-intro.mp3`.

## Output della skill

### Nuovo file `podcast/<slug>-intro.txt`

- 2–4 frasi: saluto + hook che incuriosisce sull'argomento dell'episodio (tono teaser).
- Stesse regole "per l'orecchio" dei chunk: prima persona, stile parlato, nessun audio
  tag fra parentesi quadre, `<break time="…"/>` ammesso, nessun riferimento visivo,
  nessun Markdown/header, **stessa lingua del post**.
- È testo puro pronto per la TTS, come i chunk.

### Chunk `-NN.txt`

- Non aprono più con cold open / saluto / intro dell'argomento: il `-01` entra
  direttamente nel corpo.
- L'arco dell'episodio diventa: **intro (file separato) → corpo (chunk) → outro
  (nell'ultimo chunk)**.
- Regola di split, percorso e regole di stile invariati.

## Script audio (`generate_audio.py`)

- Nuova funzione pura `discover_intro(podcast_dir: Path, slug: str) -> Path | None`:
  ritorna `<podcast_dir>/<slug>-intro.txt` se esiste, altrimenti `None`.
- `discover_chunks` resta invariata (matcha solo `<slug>-<numero>.txt`, quindi NON
  cattura il file intro).
- In `main`, la lista dei file da sintetizzare diventa: l'intro (se presente) **per
  prima**, poi i chunk numerati in ordine. Ogni file è sintetizzato con la stessa
  logica esistente e scritto tramite `chunk_to_mp3_path` (già mappa `.txt` → `.mp3`,
  quindi `<slug>-intro.txt` → `<slug>-intro.mp3`).
- L'intro è **opzionale**: se non c'è il file intro, si generano solo i chunk
  (retrocompatibile con episodi generati prima di questa feature).
- Se non c'è né intro né alcun chunk: messaggio d'errore ed exit non-zero (invariato).
- Idempotenza invariata: `--force` per sovrascrivere; senza, i `.mp3` esistenti
  (intro inclusa) vengono saltati.
- Modello/formato invariati (`eleven_multilingual_v2`, `mp3_44100_128`).

## Documentazione nella skill

- Workflow e sezione struttura output: descrivere il file `-intro.txt` e il fatto che i
  chunk non ripetono il saluto.
- Regole per l'intro (teaser, 2–4 frasi, stile parlato, no tag, `<break>` ok, lingua del
  post).
- Sezione "Generazione audio (ElevenLabs)": aggiungere che viene prodotto anche
  `<slug>-intro.mp3` (l'intro è sintetizzata per prima).
- Self-check: verificare che l'intro esista e che il chunk `-01` non ripeta
  saluto/cold open/intro.

## Testing

- Nuovo test pytest per `discover_intro`: trova `<slug>-intro.txt` quando presente;
  ritorna `None` quando assente.
- I test esistenti sulle funzioni pure restano validi. La chiamata di rete resta non
  testata in automatico.

## Rigenerazione esempio (dogfood)

- Creare `podcast/hardware-ate-software-survivors-become-agents-intro.txt` (teaser 2–4
  frasi ricavato dall'attuale cold open/intro).
- Rimuovere saluto + cold open + introduzione dell'argomento dal chunk
  `hardware-ate-software-survivors-become-agents-01.txt`, che deve iniziare dal corpo.
- Nota: i `.mp3` già generati (`-01`…`-04`) diventano stale rispetto ai nuovi testi.
  La loro rigenerazione è fuori scope (richiede crediti ElevenLabs, attualmente
  esauriti).

## Fuori scope

- Generazione audio effettiva all'interno del piano (nessun credito disponibile).
- Concatenazione dei file in un unico mp3.
- Decisione sul `.gitignore` dei file `.mp3` (gestita separatamente).
- Modifica del post sorgente.
