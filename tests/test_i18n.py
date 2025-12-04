"""Tests for translation loading logic."""

from pathlib import Path

import pytest

from videomorph import main as vm_main


class DummyTranslator:
    """Fake translator to track load calls."""

    def __init__(self, responses=None):
        self._responses = responses or []
        self.calls = []

    def load(self, filename: str, directory: str = "") -> bool:
        self.calls.append((filename, directory))
        if self._responses:
            return self._responses.pop(0)
        return True


def _resolver_factory(target_dir: Path):
    def _resolver(key: str) -> Path:
        assert key == "i18n"
        return target_dir

    return _resolver


def test_load_translation_prefers_full_locale(tmp_path: Path):
    i18n_dir = tmp_path / "translations"
    i18n_dir.mkdir()
    full_path = i18n_dir / "videomorph_es_ES.qm"
    full_path.write_bytes(b"")

    translator = DummyTranslator()
    loaded = vm_main._load_translation(
        "es_ES", translator, resolver=_resolver_factory(i18n_dir)
    )

    assert loaded == full_path
    assert translator.calls == [
        (str(full_path), ""),
    ]


def test_load_translation_falls_back_to_short_locale(tmp_path: Path):
    i18n_dir = tmp_path / "translations"
    i18n_dir.mkdir()
    short_path = i18n_dir / "videomorph_es.qm"
    short_path.write_bytes(b"")

    translator = DummyTranslator()
    loaded = vm_main._load_translation(
        "es_ES", translator, resolver=_resolver_factory(i18n_dir)
    )

    assert loaded == short_path
    assert translator.calls == [
        (str(short_path), ""),
    ]


def test_load_translation_returns_none_when_missing(tmp_path: Path, capsys: pytest.CaptureFixture):
    i18n_dir = tmp_path / "translations"
    i18n_dir.mkdir()

    translator = DummyTranslator()
    loaded = vm_main._load_translation(
        "es_ES", translator, resolver=_resolver_factory(i18n_dir)
    )

    assert loaded is None
    assert translator.calls == []
    captured = capsys.readouterr()
    assert "Warning: No translation loaded" in captured.err
