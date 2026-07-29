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


def discover_intro(podcast_dir: Path, slug: str) -> Path | None:
    """Ritorna <slug>-intro.txt in podcast_dir se esiste, altrimenti None."""
    p = podcast_dir / f"{slug}-intro.txt"
    return p if p.is_file() else None


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

    from elevenlabs.client import ElevenLabs

    client = ElevenLabs(api_key=api_key)

    generated, skipped = [], []
    for txt in files_to_process:
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
