"""``fde-kit`` CLI."""

from __future__ import annotations

import os
import shlex
import subprocess
import sys
from pathlib import Path

import click

from fde_kit.scaffold import TEMPLATES, copy_template


@click.group()
def cli():
    """fde-starter-kit — list and scaffold demo templates."""


@cli.command(name="list")
def list_cmd():
    """Show available templates."""
    for t in TEMPLATES:
        click.echo(f"{t.slug:10s} — {t.title}")
        click.echo(f"           {t.description}")


@cli.command(name="init")
@click.argument("slug", type=click.Choice([t.slug for t in TEMPLATES]))
@click.argument("dest")
@click.option("--force", is_flag=True, help="overwrite existing directory")
def init_cmd(slug, dest, force):
    """Copy a template into a new project directory.

    Example:  fde-kit init rag ./my-rag-demo
    """
    path = copy_template(slug, dest, overwrite=force)
    click.echo(f"wrote template '{slug}' to {path}")
    # The project imports fde_kit.backends, so it must run under this interpreter;
    # a bare `python` misses it after `pipx install` or `uv tool install`.
    argv = [sys.executable, "app.py"]
    command = subprocess.list2cmdline(argv) if os.name == "nt" else shlex.join(argv)
    click.echo(f"next: cd {dest} && {command}")
