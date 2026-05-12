"""extract template smoke tests."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from pydantic import ValidationError

from fde_kit import MockChatBackend


def _load_extract():
    import sys

    path = Path(__file__).resolve().parents[1] / "templates" / "extract" / "app.py"
    spec = importlib.util.spec_from_file_location("_extract_app", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def test_extract_happy_path():
    ext = _load_extract()
    backend = MockChatBackend(
        responder=lambda s, m: '{"name":"Tajaddin","age":26,"role":"engineer"}'
    )
    person = ext.extract(backend, ext.Person, "Tajaddin (26) is an engineer.")
    assert person.name == "Tajaddin"
    assert person.age == 26


def test_extract_repairs_on_validation_error():
    ext = _load_extract()
    # First call: missing "age". Second call: valid.
    script = iter(
        [
            '{"name":"Eve"}',
            '{"name":"Eve","age":30}',
        ]
    )
    backend = MockChatBackend(responder=lambda s, m: next(script))
    person = ext.extract(backend, ext.Person, "Eve, 30, dev")
    assert person.age == 30
    # The retry happened — the backend was called twice.
    assert len(backend.calls) == 2


def test_extract_raises_after_two_failures():
    ext = _load_extract()
    backend = MockChatBackend(responder=lambda s, m: "definitely not JSON")
    with pytest.raises(ValidationError):
        ext.extract(backend, ext.Person, "anything")
