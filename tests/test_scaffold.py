"""scaffold + CLI tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from fde_kit import TEMPLATES, copy_template, list_templates


def test_list_templates_returns_five():
    assert len(list_templates()) == 5
    slugs = [t.slug for t in list_templates()]
    assert slugs == ["chat", "rag", "agent", "extract", "classify"]


def test_each_template_has_required_files():
    for spec in TEMPLATES:
        root = Path(__file__).resolve().parents[1] / "templates" / spec.slug
        assert (root / "app.py").is_file(), f"{spec.slug} missing app.py"
        assert (root / "README.md").is_file(), f"{spec.slug} missing README.md"


def test_copy_template_creates_dir(tmp_path):
    dest = tmp_path / "demo"
    out = copy_template("chat", dest)
    assert out == dest
    assert (dest / "app.py").is_file()
    assert (dest / "README.md").is_file()


def test_copy_template_unknown_slug_raises(tmp_path):
    with pytest.raises(ValueError):
        copy_template("nonsense", tmp_path / "x")


def test_copy_template_refuses_nonempty_without_force(tmp_path):
    dest = tmp_path / "demo"
    dest.mkdir()
    (dest / "existing.txt").write_text("hi")
    with pytest.raises(FileExistsError):
        copy_template("chat", dest)


def test_copy_template_overwrites_with_force(tmp_path):
    dest = tmp_path / "demo"
    dest.mkdir()
    (dest / "existing.txt").write_text("hi")
    copy_template("chat", dest, overwrite=True)
    assert (dest / "app.py").is_file()
    assert not (dest / "existing.txt").exists()
