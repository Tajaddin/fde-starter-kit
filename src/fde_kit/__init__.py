"""fde-starter-kit — five deploy-ready Anthropic-stack templates.

Exports:

* ``list_templates()``  — return slug + one-line description for each template.
* ``copy_template(slug, dest_dir)`` — copy a template to a fresh project dir.
* ``ChatBackend`` Protocol + ``MockChatBackend`` + ``AnthropicChatBackend`` —
  every example imports one of these, so tests can swap a Mock without
  installing anthropic.
"""

from fde_kit.backends import (
    AnthropicChatBackend,
    ChatBackend,
    MockChatBackend,
    Reply,
)
from fde_kit.scaffold import TEMPLATES, copy_template, list_templates

__all__ = [
    "AnthropicChatBackend",
    "ChatBackend",
    "MockChatBackend",
    "Reply",
    "TEMPLATES",
    "copy_template",
    "list_templates",
]
