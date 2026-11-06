"""`fde-kit init` must print a next step that works in the generated project."""

from __future__ import annotations

import os
import subprocess
import sys

import pytest
from click.testing import CliRunner

from fde_kit import TEMPLATES
from fde_kit.cli import cli


@pytest.mark.parametrize("slug", [t.slug for t in TEMPLATES])
def test_init_prints_a_next_step_that_runs(tmp_path, slug):
    dest = tmp_path / "demo"
    result = CliRunner().invoke(cli, ["init", slug, str(dest)])
    assert result.exit_code == 0, result.output
    hint = result.output.splitlines()[-1]
    prefix = f"next: cd {dest} && "
    assert hint.startswith(prefix)
    # Bare `python` is often not the interpreter fde-kit runs in (pipx, uv tool
    # install), so the hint must name this one, quoted for the platform shell.
    assert sys.executable in hint

    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    run = subprocess.run(
        hint[len(prefix):], shell=True, cwd=dest, env=env,
        stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=60,
    )
    assert run.returncode == 0, run.stderr
    assert run.stdout.strip()


def test_init_rejects_unknown_slug(tmp_path):
    result = CliRunner().invoke(cli, ["init", "..", str(tmp_path / "demo")])
    assert result.exit_code != 0
    assert not (tmp_path / "demo").exists()
