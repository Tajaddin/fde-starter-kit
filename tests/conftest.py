"""Add the templates directory to sys.path so per-template app.py modules
import cleanly under pytest."""

from __future__ import annotations

import sys
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parents[1] / "src" / "fde_kit" / "templates"
sys.path.insert(0, str(TEMPLATES / "chat"))
sys.path.insert(0, str(TEMPLATES / "rag"))
sys.path.insert(0, str(TEMPLATES / "agent"))
sys.path.insert(0, str(TEMPLATES / "extract"))
sys.path.insert(0, str(TEMPLATES / "classify"))
