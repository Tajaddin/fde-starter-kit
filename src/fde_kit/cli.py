"""``fde-kit`` CLI."""

from __future__ import annotations

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
@click.argument("slug")
@click.argument("dest")
@click.option("--force", is_flag=True, help="overwrite existing directory")
def init_cmd(slug, dest, force):
    """Copy a template into a new project directory.

    Example:  fde-kit init rag ./my-rag-demo
    """
    path = copy_template(slug, dest, overwrite=force)
    click.echo(f"wrote template '{slug}' to {path}")
    click.echo(f"next: cd {dest} && pip install -e '.[dev]' && pytest")
