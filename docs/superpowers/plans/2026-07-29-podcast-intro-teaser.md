# File intro (teaser) per episodio podcast — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** La skill `write-podcast-script` genera un file intro separato `podcast/<slug>-intro.txt` (teaser: saluto + hook), sposta lì il saluto/intro (i chunk entrano dritti nel corpo), e `generate_audio.py` produce anche `podcast/<slug>-intro.mp3`.

**Architecture:** Tre parti. (1) Estendere lo script Python con `discover_intro` e sintetizzare l'intro per prima (funzione pura + test). (2) Aggiornare il file di istruzioni `SKILL.md`. (3) Rigenerare l'esempio: creare l'intro e togliere il saluto dal chunk `-01`.

**Tech Stack:** Python 3.12 (venv del progetto), SDK `elevenlabs`, `pytest`, Markdown (SKILL.md).

## Global Constraints

- File intro: `podcast/<slug>-intro.txt` → audio `podcast/<slug>-intro.mp3`.
- Intro = teaser 2–4 frasi (saluto + hook sull'argomento), stile parlato, prima persona, nessun audio tag `[...]`, `<break time="…"/>` ammesso, niente Markdown/header/riferimenti visivi, **lingua del post**.
- I chunk `-NN.txt` NON ripetono saluto/cold open/intro; il `-01` inizia dal corpo.
- L'intro è OPZIONALE nello script audio (se assente, si generano solo i chunk); errore solo se non c'è né intro né chunk.
- L'intro è sintetizzata PRIMA dei chunk. Modello `eleven_multilingual_v2`, formato `mp3_44100_128` invariati.
- Idempotenza invariata (`--force`; senza, salta i `.mp3` esistenti).
- Comandi Python via venv del progetto: da dentro `.claude/skills/write-podcast-script/`, usare `../../../venv/bin/python`.
- Non modificare il post sorgente. Non rigenerare audio nel piano (crediti esauriti).
- Spec: `docs/superpowers/specs/2026-07-29-podcast-intro-teaser-design.md`.

---

### Task 1: `discover_intro` nello script audio + integrazione in main

**Files:**
- Modify: `.claude/skills/write-podcast-script/generate_audio.py`
- Modify: `.claude/skills/write-podcast-script/test_generate_audio.py`

**Interfaces:**
- Consumes: funzioni esistenti `discover_chunks(podcast_dir, slug) -> list[Path]`, `chunk_to_mp3_path(txt_path) -> Path`.
- Produces: `discover_intro(podcast_dir: Path, slug: str) -> Path | None` (ritorna `<slug>-intro.txt` se esiste, altrimenti `None`); `main` sintetizza l'intro (se presente) prima dei chunk.

- [ ] **Step 1: Aggiungere i test (falliranno)**

Aggiungere in `test_generate_audio.py` questi test (in fondo al file):

```python
def test_discover_intro_found(tmp_path):
    _write(tmp_path / "foo-intro.txt")
    assert ga.discover_intro(tmp_path, "foo") == tmp_path / "foo-intro.txt"


def test_discover_intro_absent(tmp_path):
    _write(tmp_path / "foo-01.txt")
    assert ga.discover_intro(tmp_path, "foo") is None


def test_discover_chunks_excludes_intro(tmp_path):
    _write(tmp_path / "foo-intro.txt")
    _write(tmp_path / "foo-01.txt")
    assert [p.name for p in ga.discover_chunks(tmp_path, "foo")] == ["foo-01.txt"]
```

- [ ] **Step 2: Eseguire i test e verificare che falliscano**

Run: `cd .claude/skills/write-podcast-script && ../../../venv/bin/python -m pytest test_generate_audio.py -v`
Expected: FAIL — `AttributeError: module 'generate_audio' has no attribute 'discover_intro'` sui due test dell'intro (il terzo, `excludes_intro`, potrebbe già passare).

- [ ] **Step 3: Aggiungere `discover_intro` allo script**

In `generate_audio.py`, subito DOPO la funzione `discover_chunks` (prima di `chunk_to_mp3_path`), inserire:

```python
def discover_intro(podcast_dir: Path, slug: str) -> Path | None:
    """Ritorna <slug>-intro.txt in podcast_dir se esiste, altrimenti None."""
    p = podcast_dir / f"{slug}-intro.txt"
    return p if p.is_file() else None
```

- [ ] **Step 4: Integrare l'intro in `main`**

In `generate_audio.py`, sostituire questo blocco:

```python
    podcast_dir = Path(args.podcast_dir)
    chunks = discover_chunks(podcast_dir, args.slug)
    if not chunks:
        print(
            f"Nessun file {args.slug}-NN.txt in {podcast_dir}. Genera prima gli script.",
            file=sys.stderr,
        )
        return 1
```

con:

```python
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
```

Poi cambiare la riga del loop da `for txt in chunks:` a `for txt in files_to_process:`.

- [ ] **Step 5: Eseguire i test e verificare che passino**

Run: `cd .claude/skills/write-podcast-script && ../../../venv/bin/python -m pytest test_generate_audio.py -v`
Expected: PASS (tutti i test, inclusi i 3 nuovi). I test non importano `elevenlabs` (import dentro `main`), quindi passano senza la dipendenza.

- [ ] **Step 6: Commit**

```bash
git add .claude/skills/write-podcast-script/generate_audio.py .claude/skills/write-podcast-script/test_generate_audio.py
git commit -m "feat: generate_audio.py genera anche l'intro (<slug>-intro.mp3, per prima)"
```

---

### Task 2: Documentare il file intro in SKILL.md

**Files:**
- Modify: `.claude/skills/write-podcast-script/SKILL.md`

**Interfaces:**
- Consumes: lo script aggiornato (Task 1) — l'intro è generata prima dei chunk e produce `<slug>-intro.mp3`.
- Produces: skill che istruisce a creare `podcast/<slug>-intro.txt` e a non ripetere il saluto nei chunk.

- [ ] **Step 1: Aggiungere il file intro nel Workflow**

Nella sezione Workflow (il passo che scrive l'output in `podcast/<slug>-NN.txt`), aggiungere che va creato anche il file intro. Inserire un punto con questo testo:

```
- Genera inoltre `podcast/<slug>-intro.txt`: un teaser breve (2–4 frasi) con saluto +
  hook accattivante sull'argomento dell'episodio. Il saluto e l'introduzione stanno SOLO
  qui: i chunk `-NN.txt` NON aprono più con cold open/saluto/intro — il `-01` inizia
  direttamente dal corpo.
```

- [ ] **Step 2: Aggiungere le regole di stile dell'intro**

Aggiungere una breve sezione `## Intro (teaser)` (dopo la sezione sulla struttura dell'output):

```
## Intro (teaser)

`podcast/<slug>-intro.txt` è un teaser di 2–4 frasi: saluto + un hook che incuriosisce
sull'argomento (tono da trailer). Stesse regole degli altri file: prima persona, stile
parlato, nessun audio tag fra parentesi quadre, `<break time="…"/>` ammesso, nessun
riferimento visivo, nessun Markdown/header, stessa lingua del post. È testo puro pronto
per la TTS.
```

- [ ] **Step 3: Aggiornare il Self-check**

Aggiungere al blocco Self-check queste due voci:

```
- Esiste `podcast/<slug>-intro.txt` (teaser 2–4 frasi: saluto + hook).
- Il chunk `-01` NON ripete saluto/cold open/intro: inizia dal corpo.
```

- [ ] **Step 4: Aggiornare la sezione "Generazione audio (ElevenLabs)"**

Nella sezione della generazione audio, aggiungere che viene prodotto anche l'audio dell'intro. Inserire questa frase nel punto in cui si descrive l'output:

```
Viene generato anche `podcast/<slug>-intro.mp3` (l'intro è sintetizzata per prima).
```

- [ ] **Step 5: Verifica coerenza**

Run: `grep -nE "intro" .claude/skills/write-podcast-script/SKILL.md`
Expected: match nel Workflow, nella sezione `## Intro (teaser)`, nel self-check e nella sezione audio — coerenti con `podcast/<slug>-intro.txt` / `-intro.mp3`. Nessuna contraddizione (es. un punto che dice ancora che il chunk -01 apre con il saluto).

- [ ] **Step 6: Commit**

```bash
git add .claude/skills/write-podcast-script/SKILL.md
git commit -m "docs: documenta il file intro (teaser) e l'audio dell'intro nella skill"
```

---

### Task 3: Rigenerare l'esempio con file intro

**Files:**
- Create: `podcast/hardware-ate-software-survivors-become-agents-intro.txt`
- Modify: `podcast/hardware-ate-software-survivors-become-agents-01.txt`
- Read (non modificare): `content/hardware-ate-software-survivors-become-agents.md`

**Interfaces:**
- Consumes: le regole dell'intro dal Task 2.
- Produces: l'esempio d'esempio con intro separata e chunk `-01` che inizia dal corpo.

- [ ] **Step 1: Creare il file intro dell'esempio**

Leggere l'attuale `podcast/hardware-ate-software-survivors-become-agents-01.txt` (contiene il cold open + il saluto "Hey, I'm Sam…" + l'introduzione dell'argomento). Creare `podcast/hardware-ate-software-survivors-become-agents-intro.txt` con un teaser di 2–4 frasi in inglese (lingua del post): saluto + hook sull'argomento (l'idea che l'hardware "mangia" il software ma i sopravvissuti diventano agenti). Testo parlato puro, nessun audio tag, `<break>` ammesso, niente Markdown.

- [ ] **Step 2: Togliere saluto/cold open/intro dal chunk -01**

Modificare `podcast/hardware-ate-software-survivors-become-agents-01.txt` rimuovendo la parte iniziale di cold open + saluto + introduzione dell'argomento (quella ora spostata nell'intro), così che il file inizi direttamente dal corpo del discorso. Non alterare il resto del testo parlato del corpo.

- [ ] **Step 3: Verificare**

Run: `grep -nE "\[[a-zA-Z ]+\]" podcast/hardware-ate-software-survivors-become-agents-intro.txt`
Expected: nessun match (nessun audio tag nell'intro).

Run: `wc -c podcast/hardware-ate-software-survivors-become-agents-intro.txt`
Expected: file breve (indicativamente 150–600 caratteri: 2–4 frasi).

Run: `wc -c podcast/hardware-ate-software-survivors-become-agents-01.txt`
Expected: ancora < 3000 e > 250 caratteri dopo la rimozione.

Verificare a lettura che il `-01` inizi dal corpo (niente "Hey, I'm Sam"/saluto) e che l'intro contenga saluto + hook.

- [ ] **Step 4: Commit**

```bash
git add podcast/hardware-ate-software-survivors-become-agents-intro.txt podcast/hardware-ate-software-survivors-become-agents-01.txt
git commit -m "test: esempio con file intro (teaser) e chunk -01 dal corpo"
```

---

## Self-Review

**Spec coverage:**
- File intro `<slug>-intro.txt` teaser 2–4 frasi → Task 2 Steps 1-2, Task 3 Step 1. ✓
- Saluto/intro spostati; chunk -01 dal corpo → Task 2 Step 1,3, Task 3 Step 2. ✓
- `discover_intro` + intro sintetizzata per prima; opzionale; errore solo se nulla → Task 1 Steps 3-4. ✓
- `<slug>-intro.mp3` via `chunk_to_mp3_path` (riuso) → Task 1 Step 4 (loop su files_to_process). ✓
- Idempotenza/`--force`/modello/formato invariati → non modificati (loop e synthesize invariati). ✓
- Test `discover_intro` (trova / None) + esclusione dai chunk → Task 1 Step 1. ✓
- Doc skill (workflow, intro rules, self-check, audio) → Task 2. ✓
- Regole intro (no tag, `<break>`, lingua post, no Markdown) → Task 2 Step 2, Task 3 Steps 1,3. ✓
- Non rigenerare audio / non toccare sorgente → nessun task lo fa. ✓

**Placeholder scan:** nessun TBD/TODO; codice e comandi concreti in ogni step.

**Type consistency:** `discover_intro(podcast_dir, slug) -> Path | None`, `files_to_process`, `chunk_to_mp3_path` coincidono tra test (Task 1 Step 1), implementazione (Steps 3-4) e doc (Task 2).
