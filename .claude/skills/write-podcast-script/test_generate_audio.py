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
