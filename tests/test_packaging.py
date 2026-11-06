"""The wheel must carry the templates, or `fde-kit init` fails outside a checkout."""

from __future__ import annotations

import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from fde_kit import TEMPLATES

ROOT = Path(__file__).resolve().parents[1]


def test_wheel_contains_every_template(tmp_path):
    pytest.importorskip("setuptools")
    project = tmp_path / "project"
    shutil.copytree(
        ROOT / "src", project / "src", ignore=shutil.ignore_patterns("__pycache__", "*.egg-info")
    )
    for name in ("pyproject.toml", "README.md", "LICENSE"):
        shutil.copy(ROOT / name, project / name)

    build = subprocess.run(
        [sys.executable, "-c", "import setuptools.build_meta as b; print(b.build_wheel('dist'))"],
        cwd=project, capture_output=True, text=True, check=True,
    )
    wheel = project / "dist" / build.stdout.strip().splitlines()[-1]
    names = set(zipfile.ZipFile(wheel).namelist())

    for spec in TEMPLATES:
        assert f"fde_kit/templates/{spec.slug}/app.py" in names, f"{spec.slug} missing from wheel"
        assert f"fde_kit/templates/{spec.slug}/README.md" in names
    assert "fde_kit/templates/rag/corpus.json" in names
    assert not any("__pycache__" in n for n in names)
