# Chunk 40000 + retry-on-quota per `write-podcast-script` — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Portare la soglia di split a < 40000 caratteri per chunk (vincolante), riaccorpare l'esempio in un unico file, e aggiungere a `generate_audio.py` un retry-on-quota `--wait` (con safety cap e lettura della data di reset) più un guard sui 40000.

**Architecture:** Due file toccati (`generate_audio.py` + `SKILL.md`) più i `.txt` d'esempio. Nello script si aggiungono funzioni pure testabili (guard, parsing reset, classificazione errori, calcolo attesa) e una funzione di rete per la subscription; `main` acquisisce il loop `--wait` e il guard. La skill documenta la nuova soglia e il passo audio.

**Tech Stack:** Python 3.12 (venv del progetto), SDK `elevenlabs`, `urllib` (stdlib), `pytest`, Markdown (SKILL.md).

## Global Constraints

- Vincolo vincolante: ogni file (intro e ogni chunk) < 40000 caratteri.
- Soglia di split: < 40000 caratteri (sostituisce ~3000). Episodio di norma in un solo `podcast/<slug>-01.txt`.
- `--wait` attende SOLO su `quota_exceeded`; altri errori falliscono subito.
- Reset letto da `GET /v1/user/subscription` (`urllib`), campo `next_character_count_reset_unix`; serve chiave con permesso `user_read`.
- Exit codes: 1 = nessun file; 2 = config env mancante; 3 = errore API non-quota; 4 = reset non leggibile / attesa oltre max; 5 = cap cicli raggiunto (incompleto); 6 = file oltre 40000.
- Default: `--max-cycles 4`, `--max-wait-seconds 2764800`.
- Modello `eleven_multilingual_v2`, formato `mp3_44100_128`, idempotenza (`--force`, skip esistenti): invariati.
- Comandi Python via venv: da dentro `.claude/skills/write-podcast-script/`, usare `../../../venv/bin/python`.
- Non modificare il post sorgente. Non rigenerare `.mp3` nel piano.
- Spec: `docs/superpowers/specs/2026-07-29-podcast-chunk40k-and-retry-design.md`.

---

### Task 1: Funzioni pure + helper subscription (con test)

**Files:**
- Modify: `.claude/skills/write-podcast-script/generate_audio.py`
- Modify: `.claude/skills/write-podcast-script/test_generate_audio.py`

**Interfaces:**
- Consumes: nulla di nuovo.
- Produces:
  - `oversize_files(paths: list[Path], limit: int = 40000) -> list[Path]`
  - `parse_reset_unix(payload: dict) -> int | None`
  - `classify_error(exc) -> str`
  - `seconds_until(reset_unix: int, now: float) -> int`
  - `fetch_subscription(api_key: str) -> dict` (rete, non testata)

- [ ] **Step 1: Scrivere i test (falliranno)**

Aggiungere in fondo a `test_generate_audio.py`:

```python
def test_oversize_files_flags_large(tmp_path):
    small = tmp_path / "a.txt"
    small.write_text("x" * 100, encoding="utf-8")
    big = tmp_path / "b.txt"
    big.write_text("x" * 40000, encoding="utf-8")
    assert ga.oversize_files([small, big]) == [big]


def test_oversize_files_all_ok(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("x" * 39999, encoding="utf-8")
    assert ga.oversize_files([p]) == []


def test_parse_reset_unix_present():
    assert ga.parse_reset_unix({"next_character_count_reset_unix": 1750000000}) == 1750000000


def test_parse_reset_unix_absent():
    assert ga.parse_reset_unix({"foo": 1}) is None
    assert ga.parse_reset_unix({"detail": {"code": "x"}}) is None


def test_classify_error_quota():
    class E:
        body = {"detail": {"code": "quota_exceeded"}}
    assert ga.classify_error(E()) == "quota_exceeded"


def test_classify_error_unknown():
    class E:
        body = None
    assert ga.classify_error(E()) == "unknown"


def test_seconds_until_future():
    assert ga.seconds_until(1000, 400) == 600


def test_seconds_until_past():
    assert ga.seconds_until(1000, 2000) == 0
```

- [ ] **Step 2: Eseguire i test e verificare che falliscano**

Run: `cd .claude/skills/write-podcast-script && ../../../venv/bin/python -m pytest test_generate_audio.py -v`
Expected: FAIL — `AttributeError: module 'generate_audio' has no attribute 'oversize_files'` (e simili) sui nuovi test.

- [ ] **Step 3: Aggiungere le funzioni allo script**

In `generate_audio.py`, subito DOPO la funzione `synthesize` (prima di `def main`), inserire:

```python
def oversize_files(paths: list[Path], limit: int = 40000) -> list[Path]:
    """Ritorna i file il cui testo è >= limit caratteri."""
    return [p for p in paths if len(p.read_text(encoding="utf-8")) >= limit]


def parse_reset_unix(payload: dict) -> int | None:
    """Estrae next_character_count_reset_unix dal payload subscription."""
    if not isinstance(payload, dict):
        return None
    v = payload.get("next_character_count_reset_unix")
    if isinstance(v, (int, float)):
        return int(v)
    return None


def classify_error(exc) -> str:
    """Estrae il codice d'errore ElevenLabs da un'eccezione dell'SDK."""
    body = getattr(exc, "body", None)
    if isinstance(body, dict):
        detail = body.get("detail")
        if isinstance(detail, dict):
            code = detail.get("code")
            if isinstance(code, str):
                return code
    return "unknown"


def seconds_until(reset_unix: int, now: float) -> int:
    """Secondi (non negativi) da now al reset."""
    return max(0, int(reset_unix - now))


def fetch_subscription(api_key: str) -> dict:
    """GET /v1/user/subscription. Funzione di rete (non testata)."""
    import json
    import urllib.request

    req = urllib.request.Request(
        "https://api.elevenlabs.io/v1/user/subscription",
        headers={"xi-api-key": api_key},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))
```

- [ ] **Step 4: Eseguire i test e verificare che passino**

Run: `cd .claude/skills/write-podcast-script && ../../../venv/bin/python -m pytest test_generate_audio.py -v`
Expected: PASS (tutti, inclusi i nuovi). I test non toccano la rete.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/write-podcast-script/generate_audio.py .claude/skills/write-podcast-script/test_generate_audio.py
git commit -m "feat: funzioni pure per guard 40000, reset quota e classificazione errori"
```

---

### Task 2: Integrare guard e retry `--wait` in main

**Files:**
- Modify: `.claude/skills/write-podcast-script/generate_audio.py`

**Interfaces:**
- Consumes: `oversize_files`, `parse_reset_unix`, `classify_error`, `seconds_until`, `fetch_subscription` (Task 1); `discover_intro`, `discover_chunks`, `chunk_to_mp3_path`, `synthesize`, `load_config` (esistenti).
- Produces: `main` con flag `--wait`, `--max-cycles`, `--max-wait-seconds`, guard 40000 e loop di retry.

- [ ] **Step 1: Sostituire l'intera funzione `main`**

In `generate_audio.py`, sostituire l'attuale funzione `main` (da `def main(argv: list[str] | None = None) -> int:` fino a `    return 0` incluso) con:

```python
def main(argv: list[str] | None = None) -> int:
    import os
    import time
    from datetime import datetime

    parser = argparse.ArgumentParser(description="Genera audio podcast via ElevenLabs.")
    parser.add_argument("slug", help="slug dell'episodio (file podcast/<slug>-NN.txt)")
    parser.add_argument("--podcast-dir", default="podcast", help="cartella dei file")
    parser.add_argument(
        "--force", action="store_true", help="sovrascrive i .mp3 esistenti"
    )
    parser.add_argument(
        "--wait", action="store_true",
        help="su quota esaurita, attende il reset e riprova",
    )
    parser.add_argument(
        "--max-cycles", type=int, default=4,
        help="numero massimo di cicli attesa+retry con --wait",
    )
    parser.add_argument(
        "--max-wait-seconds", type=int, default=2764800,
        help="attesa massima per singolo reset (default ~32 giorni)",
    )
    args = parser.parse_args(argv)

    try:
        api_key, voice_id = load_config(os.environ)
    except ValueError as e:
        print(f"Errore di configurazione: {e}", file=sys.stderr)
        return 2

    podcast_dir = Path(args.podcast_dir)
    intro = discover_intro(podcast_dir, args.slug)
    chunks = discover_chunks(podcast_dir, args.slug)
    files_to_process = ([intro] if intro else []) + chunks
    if not files_to_process:
        print(
            f"Nessun file {args.slug}-intro.txt o {args.slug}-NN.txt in {podcast_dir}. "
            f"Genera prima gli script.",
            file=sys.stderr,
        )
        return 1

    too_big = oversize_files(files_to_process)
    if too_big:
        names = ", ".join(p.name for p in too_big)
        print(
            f"File oltre il limite di 40000 caratteri: {names}. "
            f"Riduci il testo (ElevenLabs rifiuterebbe la richiesta).",
            file=sys.stderr,
        )
        return 6

    from elevenlabs.client import ElevenLabs

    client = ElevenLabs(api_key=api_key)

    generated: list[str] = []
    skipped: list[str] = []
    cycles = 0
    while True:
        hit_quota = False
        for txt in files_to_process:
            mp3 = chunk_to_mp3_path(txt)
            if mp3.exists() and not args.force:
                if mp3.name not in skipped:
                    skipped.append(mp3.name)
                    print(f"salto {mp3.name} (esiste già; usa --force per sovrascrivere)")
                continue
            text = txt.read_text(encoding="utf-8")
            try:
                data = synthesize(client, text, voice_id)
            except Exception as e:
                if classify_error(e) == "quota_exceeded" and args.wait:
                    hit_quota = True
                    break
                print(f"Errore ElevenLabs su {txt.name}: {e}", file=sys.stderr)
                return 3
            mp3.write_bytes(data)
            generated.append(mp3.name)
            print(f"scritto {mp3.name}")

        if not hit_quota:
            break

        if cycles >= args.max_cycles:
            print(
                f"Quota esaurita e raggiunto il limite di {args.max_cycles} cicli: "
                f"episodio incompleto.",
                file=sys.stderr,
            )
            return 5

        try:
            sub = fetch_subscription(api_key)
        except Exception as e:
            print(f"Impossibile leggere la subscription: {e}", file=sys.stderr)
            return 4
        reset = parse_reset_unix(sub)
        if reset is None:
            print(
                "Data di reset non disponibile (serve una chiave con permesso user_read).",
                file=sys.stderr,
            )
            return 4
        wait_s = seconds_until(reset, time.time())
        if wait_s > args.max_wait_seconds:
            print(
                f"Attesa richiesta ({wait_s}s) oltre il massimo consentito "
                f"({args.max_wait_seconds}s): esco.",
                file=sys.stderr,
            )
            return 4
        cycles += 1
        when = datetime.fromtimestamp(reset).isoformat(timespec="minutes")
        print(
            f"Quota esaurita. Reset previsto: {when} (~{wait_s // 3600} ore). "
            f"Attendo… (ciclo {cycles}/{args.max_cycles}).",
        )
        time.sleep(wait_s + 60)

    print(f"Fatto. Generati: {len(generated)}; saltati: {len(skipped)}.")
    return 0
```

- [ ] **Step 2: Verificare che i test restino verdi**

Run: `cd .claude/skills/write-podcast-script && ../../../venv/bin/python -m pytest test_generate_audio.py -q`
Expected: PASS (le funzioni pure non sono cambiate; main non è unit-testato ma l'import del modulo deve funzionare).

- [ ] **Step 3: Verificare che lo script si avvii (smoke, senza rete)**

Run: `cd .claude/skills/write-podcast-script && ../../../venv/bin/python generate_audio.py --help`
Expected: stampa l'usage con le nuove opzioni `--wait`, `--max-cycles`, `--max-wait-seconds` (nessuna eccezione di import/sintassi).

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/write-podcast-script/generate_audio.py
git commit -m "feat: retry-on-quota --wait con safety cap e guard 40000 in main"
```

---

### Task 3: Aggiornare SKILL.md (soglia 40000 + doc --wait)

**Files:**
- Modify: `.claude/skills/write-podcast-script/SKILL.md`

**Interfaces:**
- Consumes: i flag reali dello script (Task 2) e i codici d'uscita.
- Produces: skill con soglia 40000 documentata e vincolante, e passo audio aggiornato.

- [ ] **Step 1: Aggiornare la "Regola di split"**

Nella sezione `## Regola di split`, sostituire il riferimento a ~3.000 caratteri con 40000. Il testo deve diventare:

```
- Ogni file resta sotto 40000 caratteri (limite vincolante: 1 credito ElevenLabs ≈ 1 carattere).
- Di norma l'episodio sta in UN solo `podcast/<slug>-01.txt`; si splitta in `-02`, `-03`, …
  solo se il testo supererebbe 40000 caratteri.
- Quando serve tagliare: solo su confini naturali (fine frase o paragrafo), mai dentro un
  `<break>`. Evita code sotto ~250 caratteri.
```

- [ ] **Step 2: Aggiornare "Struttura dell'output" e Common Mistakes**

Nella sezione `## Struttura dell'output` e nella tabella Common Mistakes, sostituire ogni menzione del vecchio limite ~3.000 con 40000. In particolare, nella tabella Common Mistakes la riga sul limite deve diventare:

```
| Un file oltre 40000 caratteri | Spezza in `podcast/<slug>-NN.txt`; nessun file supera 40000. |
```

- [ ] **Step 3: Aggiungere il vincolo al Self-check**

Aggiungere/aggiornare nel blocco Self-check questa voce vincolante:

```
- Vincolante: ogni file (intro e ogni chunk) è < 40000 caratteri.
```

Rimuovere l'eventuale vecchia voce che citava il limite ~3.000.

- [ ] **Step 4: Aggiornare la sezione "Generazione audio (ElevenLabs)"**

Aggiungere alla sezione, dopo la descrizione del comando, questo blocco:

```
Retry automatico su crediti esauriti (opzionale):
  `venv/bin/python .claude/skills/write-podcast-script/generate_audio.py <slug> --wait`
  Con `--wait`, se la quota è esaurita lo script legge la data di reset e attende, poi
  riprende (idempotente). Opzioni: `--max-cycles N` (default 4), `--max-wait-seconds S`
  (default ~32 giorni). Interrompibile con Ctrl-C.
  Nota: `--wait` richiede una chiave ElevenLabs con permesso `user_read` (per leggere la
  data di reset); senza, lo script esce spiegando cosa manca.
Lo script rifiuta file oltre 40000 caratteri senza chiamare l'API.
```

- [ ] **Step 5: Verifica coerenza**

Run: `grep -nE "3\.?000|40000|--wait|user_read" .claude/skills/write-podcast-script/SKILL.md`
Expected: nessun riferimento residuo a 3000/3.000 come limite di split; presenti 40000, `--wait`, `user_read`, coerenti coi nomi reali dello script.

- [ ] **Step 6: Commit**

```bash
git add .claude/skills/write-podcast-script/SKILL.md
git commit -m "docs: soglia chunk 40000 (vincolante) e documenta --wait/guard nella skill"
```

---

### Task 4: Riaccorpare l'esempio in un unico chunk

**Files:**
- Modify: `podcast/hardware-ate-software-survivors-become-agents-01.txt`
- Delete: `podcast/hardware-ate-software-survivors-become-agents-02.txt` … `-06.txt`

**Interfaces:**
- Consumes: la nuova soglia 40000 (Task 3).
- Produces: esempio con un solo chunk `-01.txt` (< 40000) + intro separata.

- [ ] **Step 1: Concatenare i 6 chunk in -01**

Unire, NELL'ORDINE 01→06, il contenuto dei file
`podcast/hardware-ate-software-survivors-become-agents-01.txt` … `-06.txt` in un unico
`-01.txt`. Preservare i `<break>` esistenti; fra il testo di un file e il successivo
lasciare una riga vuota (o un `<break time="1.0s"/>` se già presente al confine). NON
modificare il testo parlato né l'intro. NON toccare `-intro.txt` né il post sorgente.

- [ ] **Step 2: Rimuovere i chunk 02–06**

Run: `git rm podcast/hardware-ate-software-survivors-become-agents-0[2-6].txt`

- [ ] **Step 3: Verificare**

Run: `wc -c podcast/hardware-ate-software-survivors-become-agents-01.txt`
Expected: < 40000 caratteri (atteso ~14000) e > 250.

Run: `grep -nE "\[[a-zA-Z ]+\]" podcast/hardware-ate-software-survivors-become-agents-01.txt`
Expected: nessun match (nessun audio tag).

Run: `ls podcast/hardware-ate-software-survivors-become-agents-*.txt`
Expected: solo `-intro.txt` e `-01.txt`.

- [ ] **Step 4: Commit**

```bash
git add -A podcast/
git commit -m "test: esempio riaccorpato in un unico chunk (< 40000 caratteri)"
```

---

## Self-Review

**Spec coverage:**
- Soglia split 40000 vincolante → Task 3 Steps 1,3; guard `oversize_files` Task 1/2. ✓
- Riaccorpamento esempio → Task 4. ✓
- `--wait` retry su quota, idempotente → Task 2 Step 1. ✓
- Safety cap `--max-cycles`/`--max-wait-seconds` → Task 2 Step 1. ✓
- Reset via subscription + `parse_reset_unix`; user_read → Task 1 (funzioni), Task 2 (uso), Task 3 Step 4 (doc). ✓
- `classify_error` (solo quota attende) → Task 1 + Task 2. ✓
- Guard 40000 nello script (exit 6) → Task 2 Step 1. ✓
- Exit codes 1/2/3/4/5/6 → Task 2 Step 1. ✓
- Test funzioni pure → Task 1 Step 1. ✓
- Doc skill (--wait, user_read, guard) → Task 3 Step 4. ✓
- Non toccare sorgente / non rigenerare mp3 → nessun task lo fa. ✓

**Placeholder scan:** nessun TBD/TODO; codice e comandi concreti in ogni step.

**Type consistency:** `oversize_files(paths, limit=40000)`, `parse_reset_unix(payload)->int|None`, `classify_error(exc)->str`, `seconds_until(reset_unix, now)->int`, `fetch_subscription(api_key)->dict` coincidono tra i test (Task 1), l'uso in `main` (Task 2) e la doc (Task 3). Codici d'uscita coerenti col blocco Global Constraints.
