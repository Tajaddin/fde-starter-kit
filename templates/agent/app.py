"""ReAct-style tool-use agent with two built-in tools.

Run:  python app.py
"""

from __future__ import annotations

import json
import operator
import re
from dataclasses import dataclass, field
from typing import Callable

from fde_kit.backends import ChatBackend, MockChatBackend


# --- tools ----------------------------------------------------------------

@dataclass
class Tool:
    name: str
    description: str
    fn: Callable[[str], str]


def _calc(expr: str) -> str:
    # Tiny safe calculator: numbers, +-*/(), no names.
    if not re.fullmatch(r"[0-9+\-*/().\s]+", expr):
        return "ERROR: only numbers and + - * / ( ) allowed"
    try:
        return str(eval(expr, {"__builtins__": {}}, {}))  # noqa: S307
    except Exception as exc:  # noqa: BLE001
        return f"ERROR: {exc}"


def _stub_search(query: str) -> str:
    """Stand-in for a real web search. Returns canned answers for the demo."""
    Q = query.lower()
    if "capital of france" in Q:
        return "Paris is the capital of France."
    if "tampa" in Q:
        return "Tampa is a city in Florida, United States. Population ~400,000."
    return f"(no canned result for {query!r})"


BUILTIN_TOOLS: list[Tool] = [
    Tool(name="calculate", description="Evaluate a math expression.", fn=_calc),
    Tool(name="search", description="Search the web (stubbed).", fn=_stub_search),
]


# --- agent loop -----------------------------------------------------------

_SYSTEM = (
    "You are a careful agent. Available tools:\n"
    "{tool_list}\n\n"
    "On each turn, reply with EXACTLY ONE of:\n"
    "  TOOL: <tool_name>\n  ARG: <single-line argument>\n"
    "or\n"
    "  ANSWER: <final answer>\n"
)


@dataclass
class Step:
    kind: str  # "tool" | "answer"
    name: str | None = None
    arg: str | None = None
    result: str | None = None


@dataclass
class AgentTrace:
    steps: list[Step] = field(default_factory=list)
    final_answer: str | None = None


def _format_system(tools: list[Tool]) -> str:
    listing = "\n".join(f"- {t.name}: {t.description}" for t in tools)
    return _SYSTEM.format(tool_list=listing)


_TOOL_RE = re.compile(r"TOOL:\s*(\S+)\s*\n\s*ARG:\s*(.*)", re.IGNORECASE | re.DOTALL)
_ANSWER_RE = re.compile(r"ANSWER:\s*(.*)", re.IGNORECASE | re.DOTALL)


def _parse_step(text: str) -> Step | None:
    m = _TOOL_RE.search(text)
    if m:
        return Step(kind="tool", name=m.group(1).strip(), arg=m.group(2).strip().splitlines()[0])
    m = _ANSWER_RE.search(text)
    if m:
        return Step(kind="answer", result=m.group(1).strip())
    return None


def run_agent(
    backend: ChatBackend,
    question: str,
    *,
    tools: list[Tool] | None = None,
    max_steps: int = 5,
) -> AgentTrace:
    tools = tools if tools is not None else BUILTIN_TOOLS
    tool_by_name = {t.name: t for t in tools}
    system = _format_system(tools)
    messages: list[dict] = [{"role": "user", "content": question}]
    trace = AgentTrace()

    for _ in range(max_steps):
        reply = backend.chat(system, messages)
        step = _parse_step(reply.text)
        if step is None:
            # Treat unparseable response as final answer.
            trace.final_answer = reply.text.strip()
            trace.steps.append(Step(kind="answer", result=trace.final_answer))
            return trace
        if step.kind == "answer":
            trace.final_answer = step.result
            trace.steps.append(step)
            return trace
        if step.kind == "tool":
            tool = tool_by_name.get(step.name or "")
            if tool is None:
                step.result = f"ERROR: no such tool {step.name!r}"
            else:
                step.result = tool.fn(step.arg or "")
            trace.steps.append(step)
            messages.append({"role": "assistant", "content": reply.text})
            messages.append(
                {"role": "user", "content": f"TOOL_RESULT: {step.result}"}
            )
    trace.final_answer = trace.final_answer or "(agent ran out of steps)"
    return trace


if __name__ == "__main__":
    import os

    if os.environ.get("ANTHROPIC_API_KEY"):
        from fde_kit.backends import AnthropicChatBackend
        backend = AnthropicChatBackend()
    else:
        # Deterministic mock script: call calculate, then answer.
        script = iter(
            [
                "TOOL: calculate\nARG: 7 * 6",
                "ANSWER: 42",
            ]
        )
        backend = MockChatBackend(responder=lambda s, m: next(script, "ANSWER: done"))
    tr = run_agent(backend, "What is seven times six?")
    print("answer:", tr.final_answer)
    for st in tr.steps:
        print(" -", st)
