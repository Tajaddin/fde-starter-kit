"""Structured data extraction with one repair retry.

Run:  python app.py
"""

from __future__ import annotations

import json
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from fde_kit.backends import ChatBackend, MockChatBackend


T = TypeVar("T", bound=BaseModel)


class Person(BaseModel):
    name: str
    age: int
    email: str | None = None
    role: str | None = None


_SYSTEM = (
    "You are an extraction engine. Read the user's text and return a SINGLE "
    "JSON object that matches the requested schema EXACTLY. Output ONLY the "
    "JSON, no commentary, no markdown fences."
)


def _build_prompt(schema_name: str, schema_dict: dict, text: str, error: str | None = None) -> str:
    schema_str = json.dumps(schema_dict, indent=2)
    pieces = [
        f"Schema ({schema_name}):\n```\n{schema_str}\n```",
        f"Text:\n{text}",
    ]
    if error:
        pieces.append(
            "The previous attempt was invalid. Here is the validation error — "
            f"return a corrected JSON object.\nerror: {error}"
        )
    return "\n\n".join(pieces)


def extract(backend: ChatBackend, model_cls: type[T], text: str) -> T:
    """Returns a validated instance of ``model_cls`` or raises ValidationError
    after one repair attempt."""
    schema = model_cls.model_json_schema()
    prompt = _build_prompt(model_cls.__name__, schema, text)
    reply = backend.chat(_SYSTEM, [{"role": "user", "content": prompt}])
    last_err: str | None = None
    for attempt in range(2):
        try:
            data = json.loads(reply.text)
        except json.JSONDecodeError as exc:
            last_err = f"JSONDecodeError: {exc}"
        else:
            try:
                return model_cls.model_validate(data)
            except ValidationError as exc:
                last_err = exc.json()
        if attempt == 0:
            prompt = _build_prompt(model_cls.__name__, schema, text, error=last_err)
            reply = backend.chat(_SYSTEM, [{"role": "user", "content": prompt}])
    raise ValidationError.from_exception_data(
        title=model_cls.__name__,
        line_errors=[{"type": "value_error", "loc": (), "input": reply.text, "ctx": {"error": last_err}}],
    )


if __name__ == "__main__":
    import os

    if os.environ.get("ANTHROPIC_API_KEY"):
        from fde_kit.backends import AnthropicChatBackend
        backend = AnthropicChatBackend()
    else:
        script = iter(['{"name": "Tajaddin", "age": 26, "role": "engineer"}'])
        backend = MockChatBackend(responder=lambda s, m: next(script, "{}"))

    text = "Tajaddin (26) is an engineer based in Tampa."
    person = extract(backend, Person, text)
    print(person.model_dump_json(indent=2))
