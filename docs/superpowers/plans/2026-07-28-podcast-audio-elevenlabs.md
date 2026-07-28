# Audio ElevenLabs + rimozione tag v3 per `write-podcast-script` — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** La skill `write-podcast-script` smette di produrre audio tag v3 nei `.txt` e ottiene un passo on-demand che genera un `.mp3` per chunk tramite l'SDK ElevenLabs (`eleven_multilingual_v2`).

**Architecture:** Due parti. (A) Modifica al file di istruzioni `SKILL.md` e rigenerazione dell'esempio: i `.txt` diventano testo parlato puro + `<break>`. (B) Un piccolo script Python committato con la skill (`generate_audio.py`) con logica pura testabile e un'unica funzione che tocca la rete; dipendenza `elevenlabs` isolata in un requirements separato per non toccare la CI Pelican.

**Tech Stack:** Markdown (SKILL.md), Python 3.12 (venv del progetto), SDK `elevenlabs`, `pytest`, ElevenLabs TTS `eleven_multilingual_v2`.

## Global Constraints

- Modello TTS: `eleven_multilingual_v2`; output format `mp3_44100_128`.
- I `.txt` contengono SOLO testo parlato + tag di pausa `<break time="…"/>`. Nessun audio tag fra parentesi quadre (`[...]`).
- Pause: beat breve `<break time="0.5s"/>`; confine di sezione `<break time="1.0s"/>`.
- Audio: un `.mp3` per chunk, `podcast/<slug>-NN.mp3` accanto ai `.txt`. Nessuna concatenazione.
- Generazione audio SOLO su richiesta esplicita; la generazione dei `.txt` non chiama mai l'API.
- Config solo da env: `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID`. Mai stampare/committare i valori.
- Dipendenza `elevenlabs` in `.claude/skills/write-podcast-script/requirements-audio.txt`, NON in `requirements.txt`.
- Comandi Python via il venv del progetto: `venv/bin/python`, `venv/bin/pytest`, `venv/bin/pip`.
- Regole di stile "per l'orecchio" e regola di split invariate; percorso `podcast/<slug>-NN.txt` invariato.
- Non modificare il post sorgente.
- Spec di riferimento: `docs/superpowers/specs/2026-07-28-podcast-audio-elevenlabs-design.md`.

---

### Task 1: Rimuovere gli audio tag v3 da SKILL.md

**Files:**
- Modify: `.claude/skills/write-podcast-script/SKILL.md`

**Interfaces:**
- Consumes: nulla.
- Produces: skill in cui l'unico marker ammesso nei `.txt` è `<break time="…"/>`; nessun riferimento ad audio tag o palette v3. Le sezioni toccate: "Audio tag v3" (rimossa), "Regola di split"/struttura output (pause via `<break>`), "Self-check", "Common Mistakes".

- [ ] **Step 1: Rimuovere la sezione "Audio tag v3"**

Eliminare interamente la sezione `## Audio tag v3` (titolo + corpo + palette chiusa) dal file.

- [ ] **Step 2: Aggiornare la resa delle pause nella struttura output**

Nella sezione che descrive la struttura dell'output e i confini di sezione, sostituire ogni riferimento a `[pause]` e agli audio tag con la resa via `<break>`. Il testo deve dire:

```
- I confini fra i momenti dell'episodio (cold open → intro → corpo → outro) NON sono
  scritti come marker: si rendono con una pausa `<break time="1.0s"/>`.
- Le pause brevi (un beat dentro il discorso) si rendono con `<break time="0.5s"/>`.
- Nessun audio tag fra parentesi quadre: l'unico marker ammesso nel testo è `<break time="…"/>`.
```

- [ ] **Step 3: Aggiornare il Self-check**

Nel blocco Self-check, sostituire le righe che citano gli audio tag / la palette con:

```
- Nessun audio tag fra parentesi quadre; le pause sono solo `<break time="…"/>`.
```

Mantenere invariate le altre voci (adattamento completo e in ordine, niente riferimenti visivi, acronimi espansi, numeri/simboli parlati, file 100% puliti senza header/Markdown, split < ~3.000 caratteri su confini naturali mai dentro un tag e niente code sotto ~250 caratteri, output in `podcast/<slug>-NN.txt`).

- [ ] **Step 4: Aggiornare la tabella Common Mistakes**

Rimuovere le righe che parlano di palette v3 / `[pausa]` vs `[pause]` / tag inventati. Aggiungere/mantenere queste righe:

| Mistake | Fix |
|---------|-----|
| Usare audio tag fra parentesi quadre (es. `[thoughtful]`, `[pause]`) | Nessun audio tag; le pause sono solo `<break time="…"/>`. |
| Markdown o marker di sezione nel file .txt | Solo testo parlato + `<break>`; niente header/Markdown/marker. |
| Un unico file oltre ~3.000 caratteri | Spezza in `podcast/<slug>-NN.txt` su confini naturali. |
| Writing into content/ | Scripts go to `podcast/<slug>-NN.txt`, outside content/. |

- [ ] **Step 5: Aggiornare l'esempio in fondo alla skill**

Se l'`## Example` finale mostra un audio tag (es. `[thoughtful]`), riscriverlo senza tag, mantenendo eventualmente un `<break time="1.0s"/>` finale. Esempio dell'output atteso:

```
So let's start with where the article is right. Value really is migrating. And here's
the blunt version: if your product is just a thin shell around a single model call, your
margin is a rounding error on somebody else's infrastructure bill. <break time="1.0s"/>
```

- [ ] **Step 6: Rilettura di coerenza**

Rileggere l'intero `SKILL.md`. Verificare che NON compaiano più: la parola "palette", i tag `[thoughtful]/[curious]/[serious]/[excited]/[laughs]/[sighs]/[sarcastic]/[whispers]`, né `[pause]`/`[pausa]` come istruzione (possono restare solo come esempi-da-evitare nella tabella Common Mistakes). Verificare che `<break time="…"/>` sia citato come unico marker di pausa.

Run: `grep -nE "\[(thoughtful|curious|serious|excited|laughs|sighs|sarcastic|whispers|pause|pausa)\]|palette" .claude/skills/write-podcast-script/SKILL.md`
Expected: match solo dentro la tabella Common Mistakes (righe "Fix"/"Mistake" che li citano come errori). Nessun match nelle sezioni istruttive.

- [ ] **Step 7: Commit**

```bash
git add .claude/skills/write-podcast-script/SKILL.md
git commit -m "feat: write-podcast-script non produce più audio tag v3 (solo <break>)"
```

---

### Task 2: Rigenerare l'esempio senza audio tag

**Files:**
- Modify: `podcast/hardware-ate-software-survivors-become-agents-01.txt` … `-06.txt`
- Read (non modificare): `content/hardware-ate-software-survivors-become-agents.md`

**Interfaces:**
- Consumes: la skill aggiornata dal Task 1.
- Produces: i 6 file `.txt` d'esempio senza alcun audio tag, con le pause rese via `<break>`.

- [ ] **Step 1: Rimuovere gli audio tag e convertire le pause**

Su ciascuno dei 6 file `podcast/hardware-ate-software-survivors-become-agents-*.txt`:
- Eliminare ogni audio tag fra parentesi quadre (`[thoughtful]`, `[serious]`, `[curious]`, `[excited]`, e qualunque altro tag della vecchia palette), inclusi eventuali spazi doppi risultanti.
- Convertire ogni `[pause]` in `<break time="0.5s"/>`.
- NON cambiare il testo parlato né i `<break time="1.0s"/>` già presenti ai confini di sezione.

- [ ] **Step 2: Verificare l'assenza di tag e la presenza dei break**

Run: `grep -nE "\[[a-zA-Z ]+\]" podcast/hardware-ate-software-survivors-become-agents-*.txt`
Expected: nessun match (nessun audio tag residuo).

Run: `grep -c "break time" podcast/hardware-ate-software-survivors-become-agents-*.txt`
Expected: ogni file riporta un conteggio ≥ 1 (le pause ci sono ancora, come `<break>`).

Run: `wc -c podcast/hardware-ate-software-survivors-become-agents-*.txt`
Expected: ogni file < 3000 caratteri, nessuno sotto ~250.

- [ ] **Step 3: Commit**

```bash
git add podcast/hardware-ate-software-survivors-become-agents-*.txt
git commit -m "test: rigenera esempio senza audio tag v3 (solo <break>)"
```

---

### Task 3: Script generate_audio.py con funzioni pure e test

**Files:**
- Create: `.claude/skills/write-podcast-script/generate_audio.py`
- Create: `.claude/skills/write-podcast-script/test_generate_audio.py`
- Create: `.claude/skills/write-podcast-script/requirements-audio.txt`

**Interfaces:**
- Consumes: i file `podcast/<slug>-NN.txt` (Task 1/2).
- Produces:
  - `discover_chunks(podcast_dir: Path, slug: str) -> list[Path]` — file `.txt` del podcast ordinati per numero.
  - `chunk_to_mp3_path(txt_path: Path) -> Path` — mappa `<slug>-NN.txt` → `<slug>-NN.mp3`.
  - `load_config(env: Mapping[str, str]) -> tuple[str, str]` — `(api_key, voice_id)`; solleva `ValueError` con messaggio chiaro se una manca.
  - `synthesize(client, text: str, voice_id: str) -> bytes` — unica funzione che chiama l'SDK (non testata).
  - `main(argv: list[str] | None = None) -> int` — CLI/orchestrazione.

- [ ] **Step 1: Creare il requirements isolato**

Creare `.claude/skills/write-podcast-script/requirements-audio.txt` con:

```
elevenlabs>=1.0
```

- [ ] **Step 2: Scrivere i test delle funzioni pure (falliranno)**

Creare `.claude/skills/write-podcast-script/test_generate_audio.py`:

```python
from pathlib import Path

import pytest

import generate_audio as ga


def _write(p: Path, text: str = "x") -> None:
    p.write_text(text, encoding="utf-8")


def test_discover_chunks_sorted_numerically(tmp_path):
    _write(tmp_path / "foo-02.txt")
    _write(tmp_path / "foo-10.txt")
    _write(tmp_path / "foo-01.txt")
    _write(tmp_path / "bar-01.txt")  # slug diverso, va escluso
    _write(tmp_path / "foo.md")      # non .txt, va escluso
    result = ga.discover_chunks(tmp_path, "foo")
    assert [p.name for p in result] == ["foo-01.txt", "foo-02.txt", "foo-10.txt"]


def test_discover_chunks_empty(tmp_path):
    assert ga.discover_chunks(tmp_path, "foo") == []


def test_chunk_to_mp3_path():
    assert ga.chunk_to_mp3_path(Path("podcast/foo-03.txt")) == Path("podcast/foo-03.mp3")


def test_load_config_ok():
    env = {"ELEVENLABS_API_KEY": "k", "ELEVENLABS_VOICE_ID": "v"}
    assert ga.load_config(env) == ("k", "v")


def test_load_config_missing_api_key():
    with pytest.raises(ValueError, match="ELEVENLABS_API_KEY"):
        ga.load_config({"ELEVENLABS_VOICE_ID": "v"})


def test_load_config_missing_voice_id():
    with pytest.raises(ValueError, match="ELEVENLABS_VOICE_ID"):
        ga.load_config({"ELEVENLABS_API_KEY": "k"})
```

- [ ] **Step 3: Eseguire i test e verificare che falliscano**

Run: `cd .claude/skills/write-podcast-script && ../../../venv/bin/python -m pytest test_generate_audio.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'generate_audio'` (lo script non esiste ancora).

- [ ] **Step 4: Scrivere generate_audio.py**

Creare `.claude/skills/write-podcast-script/generate_audio.py`:

```python
"""Genera un file audio .mp3 per ogni chunk .txt di un episodio podcast,
usando l'API ElevenLabs (modello eleven_multilingual_v2).

Uso:
    python generate_audio.py <slug> [--podcast-dir DIR] [--force]

Config da ambiente:
    ELEVENLABS_API_KEY   chiave API (obbligatoria)
    ELEVENLABS_VOICE_ID  voice id da usare (obbligatoria)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Mapping

MODEL_ID = "eleven_multilingual_v2"
OUTPUT_FORMAT = "mp3_44100_128"


def discover_chunks(podcast_dir: Path, slug: str) -> list[Path]:
    """Ritorna i file <slug>-NN.txt in podcast_dir, ordinati per numero."""
    pattern = re.compile(rf"^{re.escape(slug)}-(\d+)\.txt$")
    matches: list[tuple[int, Path]] = []
    for p in podcast_dir.glob(f"{slug}-*.txt"):
        m = pattern.match(p.name)
        if m:
            matches.append((int(m.group(1)), p))
    return [p for _, p in sorted(matches, key=lambda t: t[0])]


def chunk_to_mp3_path(txt_path: Path) -> Path:
    """Mappa <slug>-NN.txt -> <slug>-NN.mp3 nella stessa cartella."""
    return txt_path.with_suffix(".mp3")


def load_config(env: Mapping[str, str]) -> tuple[str, str]:
    """Legge api_key e voice_id dall'ambiente; ValueError se mancano."""
    api_key = env.get("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError(
            "ELEVENLABS_API_KEY non impostata. Esporta la chiave API ElevenLabs."
        )
    voice_id = env.get("ELEVENLABS_VOICE_ID")
    if not voice_id:
        raise ValueError(
            "ELEVENLABS_VOICE_ID non impostata. Esporta il voice id da usare."
        )
    return api_key, voice_id


def synthesize(client, text: str, voice_id: str) -> bytes:
    """Chiama l'SDK ElevenLabs e ritorna i byte mp3. Unica funzione di rete."""
    audio = client.text_to_speech.convert(
        voice_id=voice_id,
        model_id=MODEL_ID,
        text=text,
        output_format=OUTPUT_FORMAT,
    )
    return b"".join(audio)


def main(argv: list[str] | None = None) -> int:
    import os

    parser = argparse.ArgumentParser(description="Genera audio podcast via ElevenLabs.")
    parser.add_argument("slug", help="slug dell'episodio (file podcast/<slug>-NN.txt)")
    parser.add_argument("--podcast-dir", default="podcast", help="cartella dei file")
    parser.add_argument(
        "--force", action="store_true", help="sovrascrive i .mp3 esistenti"
    )
    args = parser.parse_args(argv)

    try:
        api_key, voice_id = load_config(os.environ)
    except ValueError as e:
        print(f"Errore di configurazione: {e}", file=sys.stderr)
        return 2

    podcast_dir = Path(args.podcast_dir)
    chunks = discover_chunks(podcast_dir, args.slug)
    if not chunks:
        print(
            f"Nessun file {args.slug}-NN.txt in {podcast_dir}. Genera prima gli script.",
            file=sys.stderr,
        )
        return 1

    from elevenlabs.client import ElevenLabs

    client = ElevenLabs(api_key=api_key)

    generated, skipped = [], []
    for txt in chunks:
        mp3 = chunk_to_mp3_path(txt)
        if mp3.exists() and not args.force:
            skipped.append(mp3.name)
            print(f"salto {mp3.name} (esiste già; usa --force per sovrascrivere)")
            continue
        text = txt.read_text(encoding="utf-8")
        try:
            data = synthesize(client, text, voice_id)
        except Exception as e:  # errore SDK/rete: riporta e ferma
            print(f"Errore ElevenLabs su {txt.name}: {e}", file=sys.stderr)
            return 3
        mp3.write_bytes(data)
        generated.append(mp3.name)
        print(f"scritto {mp3.name}")

    print(f"Fatto. Generati: {len(generated)}; saltati: {len(skipped)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 5: Eseguire i test e verificare che passino**

Run: `cd .claude/skills/write-podcast-script && ../../../venv/bin/python -m pytest test_generate_audio.py -v`
Expected: PASS (6 test verdi). I test non importano `elevenlabs` (l'import dell'SDK è dentro `main`), quindi passano senza installare la dipendenza.

- [ ] **Step 6: Commit**

```bash
git add .claude/skills/write-podcast-script/generate_audio.py .claude/skills/write-podcast-script/test_generate_audio.py .claude/skills/write-podcast-script/requirements-audio.txt
git commit -m "feat: script generate_audio.py (ElevenLabs TTS, un mp3 per chunk)"
```

---

### Task 4: Documentare il passo audio in SKILL.md

**Files:**
- Modify: `.claude/skills/write-podcast-script/SKILL.md`

**Interfaces:**
- Consumes: lo script `generate_audio.py` e i suoi flag dal Task 3; le env var dai Global Constraints.
- Produces: sezione di documentazione che istruisce l'agente a eseguire il passo audio on-demand.

- [ ] **Step 1: Aggiungere la sezione "Generazione audio (ElevenLabs)"**

Aggiungere in `SKILL.md` (dopo il self-check, prima di Common Mistakes) una sezione:

```
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
```

- [ ] **Step 2: Aggiornare Overview/Scope se cita solo i .txt**

Se l'Overview afferma che la skill produce "solo testo" senza audio, aggiungere una frase che rimanda al passo audio opzionale della nuova sezione. Non cambiare il resto.

- [ ] **Step 3: Verifica coerenza**

Run: `grep -nE "generate_audio\.py|ELEVENLABS_API_KEY|ELEVENLABS_VOICE_ID|requirements-audio\.txt|eleven_multilingual_v2" .claude/skills/write-podcast-script/SKILL.md`
Expected: i riferimenti al comando, alle env var, al requirements e al modello sono presenti e coerenti con i nomi reali del Task 3.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/write-podcast-script/SKILL.md
git commit -m "docs: documenta il passo di generazione audio ElevenLabs nella skill"
```

---

## Self-Review

**Spec coverage:**
- Modello `eleven_multilingual_v2` + `mp3_44100_128` → Task 3 Step 4 (costanti). ✓
- Rimozione audio tag v3 dai `.txt`/skill → Task 1 (istruzioni), Task 2 (esempio). ✓
- Pause via `<break>` (0.5s beat, 1.0s sezione) → Task 1 Step 2, Task 2 Step 1. ✓
- Trigger on-demand, i `.txt` non chiamano l'API → Task 4 Step 1. ✓
- Un `.mp3` per chunk, `podcast/<slug>-NN.mp3` → Task 3 (`chunk_to_mp3_path`, main). ✓
- SDK Python + requirements isolato (non in requirements.txt) → Task 3 Steps 1,4. ✓
- Config da env, errore chiaro se mancano, mai stampare valori → Task 3 (`load_config`, main). ✓
- Idempotenza (`--force`, skip se esiste) + prerequisito `.txt` → Task 3 Step 4 (main). ✓
- Funzioni pure testate con pytest; rete non testata → Task 3 Steps 2-5. ✓
- Documentazione del passo nella skill → Task 4. ✓
- Regole di stile/split invariate, non toccare il sorgente → non modificate; Task 1 Step 3 le preserva. ✓

**Placeholder scan:** nessun TBD/TODO; codice e comandi concreti in ogni step.

**Type consistency:** i nomi (`discover_chunks`, `chunk_to_mp3_path`, `load_config`, `synthesize`, `main`), le costanti (`MODEL_ID`, `OUTPUT_FORMAT`), le env var e i flag CLI coincidono fra i test (Task 3 Step 2), l'implementazione (Step 4) e la doc (Task 4).
