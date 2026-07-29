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
