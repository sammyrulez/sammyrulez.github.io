"""Genera un file audio .mp3 per l'intro e per ogni chunk .txt di un episodio podcast,
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


def discover_intro(podcast_dir: Path, slug: str) -> Path | None:
    """Ritorna <slug>-intro.txt in podcast_dir se esiste, altrimenti None."""
    p = podcast_dir / f"{slug}-intro.txt"
    return p if p.is_file() else None


def chunk_to_mp3_path(txt_path: Path) -> Path:
    """Mappa un file <name>.txt nel corrispondente <name>.mp3 nella stessa cartella."""
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


if __name__ == "__main__":
    raise SystemExit(main())
