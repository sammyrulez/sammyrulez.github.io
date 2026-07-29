# Design: soglia chunk 40000, riaccorpamento esempio, retry-on-quota

Data: 2026-07-29

## Contesto

La skill `write-podcast-script` produce `podcast/<slug>-intro.txt` + `podcast/<slug>-NN.txt`
(testo puro per ElevenLabs) e, su richiesta, gli `.mp3` via `generate_audio.py`
(`eleven_multilingual_v2`, un mp3 per file). La regola di split attuale impone chunk
< ~3000 caratteri.

Cambiamenti richiesti (utente passa al piano a pagamento):
1. Vincolo vincolante: **ogni chunk < 40000 caratteri** (sostituisce il limite ~3000).
2. Riaccorpare l'episodio d'esempio in un unico file coerente con la nuova soglia.
3. Aggiungere al `generate_audio.py` un loop di retry `--wait` che, su esaurimento
   crediti, attende il reset della quota e riprende.

Nota di dominio: per i modelli TTS standard ElevenLabs **1 credito ≈ 1 carattere**.

## Decisioni prese

1. Soglia di split: **ogni chunk < 40000 caratteri**, sostituisce ~3000. Di norma
   l'episodio sta in un solo `-01.txt`.
2. È **condizione vincolante** (self-check): nessun file supera 40000 caratteri.
3. Esempio: unire i 6 chunk in un unico `-01.txt`; intro separata resta.
4. `--wait`: loop bloccante di retry solo su `quota_exceeded`, con safety cap; legge la
   data di reset dall'endpoint subscription (serve chiave con `user_read`).
5. Abbandonato ogni tetto sul totale episodio (es. 15000): sostituito dal vincolo
   per-chunk < 40000.

## Parte A — Nuova soglia di split (SKILL.md)

- La sezione "Regola di split": soglia da ~3000 a **< 40000 caratteri**. L'episodio sta
  in un solo `podcast/<slug>-01.txt`; si splitta in `-02`, `-03`, … solo se il testo
  supera 40000. Il taglio, quando serve, resta su confini naturali (fine frase/paragrafo),
  mai dentro un `<break>`, evitando code sotto ~250 caratteri.
- Self-check: aggiungere/aggiornare la voce vincolante: "Ogni file (intro e ogni chunk)
  è < 40000 caratteri."
- Aggiornare i riferimenti al vecchio ~3000 (Struttura dell'output, Common Mistakes,
  eventuali esempi) alla nuova soglia 40000.
- Invariati: intro separata (teaser), testo puro + `<break>`, niente audio tag, regole
  "per l'orecchio", percorsi `podcast/<slug>-intro.txt` / `-NN.txt`.

## Parte B — Riaccorpamento esempio

- Unire il testo dei 6 file `podcast/hardware-ate-software-survivors-become-agents-01.txt`
  … `-06.txt` in un unico `podcast/hardware-ate-software-survivors-become-agents-01.txt`
  (nell'ordine 01→06), preservando i `<break>` esistenti fra le parti.
- Rimuovere `-02.txt` … `-06.txt`.
- L'intro `-intro.txt` resta invariata e separata.
- Il file risultante deve essere < 40000 caratteri (atteso ~14000).
- Gli `.mp3` esistenti diventano stale; sono git-ignorati e la loro rigenerazione è fuori
  scope (richiede crediti).

## Parte C — Retry-on-quota `--wait` (generate_audio.py)

### Comportamento

- Nuovo flag `--wait`: se una richiesta fallisce con **`quota_exceeded`**, lo script
  legge la data di reset della quota e **dorme fino ad allora** (+ piccolo buffer), poi
  ridiscopre i file e genera i `.mp3` mancanti (idempotente). Senza `--wait`,
  comportamento attuale invariato (esce su errore, codice 3).
- **Solo** `quota_exceeded` fa attendere. Altri errori (`paid_plan_required`,
  `unauthorized`/permessi, voce invalida, ecc.) falliscono subito con messaggio.
- Interrompibile con Ctrl-C; i file già scritti restano.

### Safety cap

- `--max-cycles N` (default **4**): numero massimo di cicli attesa+retry. Al
  raggiungimento con file ancora mancanti → messaggio "episodio incompleto" ed exit code
  dedicato (5).
- `--max-wait-seconds S` (default **2764800**, ~32 giorni): se il reset calcolato supera
  questo limite (valore anomalo/assente) → messaggio ed exit, niente sleep abnorme.

### Lettura data reset

- `fetch_subscription(api_key) -> dict`: GET `https://api.elevenlabs.io/v1/user/subscription`
  con header `xi-api-key`, via `urllib.request` (nessuna nuova dipendenza). Funzione di
  rete, non testata in automatico.
- `parse_reset_unix(payload: dict) -> int | None`: estrae
  `next_character_count_reset_unix` (pura, testata). Se assente → `None`.
- Se il reset non è leggibile (es. chiave senza permesso `user_read`) → messaggio chiaro
  ("serve una chiave con permesso user_read per attendere il reset") ed exit code 4;
  niente attesa alla cieca.

### Classificazione errori

- `classify_error(exc) -> str` (pura, testata): estrae `exc.body["detail"]["code"]` e
  ritorna es. `"quota_exceeded"`, `"paid_plan_required"`, `"unauthorized"`, o
  `"unknown"` se non determinabile. Il loop usa questo per decidere se attendere o fallire.

### Utility tempo

- `seconds_until(reset_unix: int, now: float) -> int`: ritorna `max(0, reset_unix - now)`
  (pura, testata).

## Guard 40000 nello script

- `oversize_files(paths: list[Path], limit: int = 40000) -> list[Path]` (pura, testata):
  ritorna i file il cui testo è ≥ `limit` caratteri.
- In `main`, prima di sintetizzare: se `oversize_files(files_to_process)` non è vuoto →
  messaggio che elenca i file troppo grandi ed exit non-zero (codice 6), senza chiamare
  l'API (l'API rifiuterebbe comunque una richiesta oltre il limite di caratteri).

## Testing (pytest, funzioni pure)

- `oversize_files`: rileva file ≥ 40000, ignora quelli sotto; lista vuota se tutti ok.
- `parse_reset_unix`: campo presente / assente / payload di errore → `None`.
- `classify_error`: quota / payment / unauthorized / unknown, con oggetto-eccezione
  fittizio che espone `.body`.
- `seconds_until`: reset futuro → positivo; reset passato → 0.
- La rete (`fetch_subscription`, `synthesize`) e lo sleep non sono testati in automatico.

## Documentazione skill

- Aggiornare "Regola di split" e "Struttura dell'output" alla soglia 40000; self-check con
  il vincolo < 40000; Common Mistakes coerente.
- Sezione "Generazione audio (ElevenLabs)": documentare `--wait`, `--max-cycles`,
  `--max-wait-seconds`; il requisito della chiave con permesso `user_read` per `--wait`;
  il guard dei 40000; il caveat che `--wait` è pensato per attese ragionevoli (piano a
  pagamento) ed è interrompibile.

## Fuori scope

- Retry schedulato/cron, notifiche push, concatenazione dei file in un unico mp3.
- Rigenerazione degli `.mp3` (richiede crediti; git-ignorati).
- Modifica del post sorgente.
