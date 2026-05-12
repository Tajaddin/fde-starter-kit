"""``fde-kit init`` engine: copy a named template into a destination dir."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TemplateSpec:
    slug: str
    title: str
    description: str


TEMPLATES: list[TemplateSpec] = [
    TemplateSpec(
        slug="chat",
        title="Conversational Chat",
        description=(
            "Multi-turn chat agent with system prompt + conversation history. "
            "FastAPI endpoint, CLI client, swappable backend."
        ),
    ),
    TemplateSpec(
        slug="rag",
        title="RAG over a JSON corpus",
        description=(
            "Embedding-free RAG using BM25 keyword retrieval over a JSON corpus. "
            "Citations are returned alongside the answer."
        ),
    ),
    TemplateSpec(
        slug="agent",
        title="ReAct-style Tool-Use Agent",
        description=(
            "Tool-calling loop with two built-in tools (calculator + web-search stub). "
            "Bounded max_steps, full trace returned."
        ),
    ),
    TemplateSpec(
        slug="extract",
        title="Structured Data Extraction",
        description=(
            "Pydantic-validated extraction from free-form text. "
            "Repairs invalid JSON via one retry with the validation error attached."
        ),
    ),
    TemplateSpec(
        slug="classify",
        title="Multi-Label Classification",
        description=(
            "LLM-as-classifier with calibration: returns label + confidence + reasoning. "
            "Includes a tiny eval harness."
        ),
    ),
]


def _templates_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        cand = parent / "templates"
        if cand.is_dir() and (cand / "chat").is_dir():
            return cand
    raise FileNotFoundError("templates/ not found")


def list_templates() -> list[TemplateSpec]:
    return list(TEMPLATES)


def copy_template(slug: str, dest_dir: str | Path, *, overwrite: bool = False) -> Path:
    src = _templates_root() / slug
    if not src.is_dir():
        valid = ", ".join(t.slug for t in TEMPLATES)
        raise ValueError(f"unknown template {slug!r}; expected one of: {valid}")
    dest = Path(dest_dir)
    if dest.exists() and any(dest.iterdir()):
        if not overwrite:
            raise FileExistsError(
                f"destination {dest} is not empty; pass overwrite=True to clobber"
            )
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    return dest
