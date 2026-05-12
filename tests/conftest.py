"""Add the templates directory to sys.path so per-template app.py modules
import cleanly under pytest."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "templates" / "chat"))
sys.path.insert(0, str(ROOT / "templates" / "rag"))
sys.path.insert(0, str(ROOT / "templates" / "agent"))
sys.path.insert(0, str(ROOT / "templates" / "extract"))
sys.path.insert(0, str(ROOT / "templates" / "classify"))
