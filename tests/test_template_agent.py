"""agent template smoke tests."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from fde_kit import MockChatBackend


def _load_agent():
    import sys

    path = Path(__file__).resolve().parents[1] / "templates" / "agent" / "app.py"
    spec = importlib.util.spec_from_file_location("_agent_app", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def test_calculator_tool_evaluates_safe_expressions():
    agent = _load_agent()
    fn = next(t.fn for t in agent.BUILTIN_TOOLS if t.name == "calculate")
    assert fn("7 * 6") == "42"


def test_calculator_rejects_unsafe_input():
    agent = _load_agent()
    fn = next(t.fn for t in agent.BUILTIN_TOOLS if t.name == "calculate")
    assert fn("__import__('os')").startswith("ERROR")


def test_agent_calls_tool_then_answers():
    agent = _load_agent()
    script = iter(
        [
            "TOOL: calculate\nARG: 7 * 6",
            "ANSWER: 42",
        ]
    )
    backend = MockChatBackend(responder=lambda s, m: next(script))
    trace = agent.run_agent(backend, "what is 7*6?")
    assert trace.final_answer == "42"
    assert any(s.kind == "tool" and s.name == "calculate" for s in trace.steps)


def test_agent_handles_unknown_tool_gracefully():
    agent = _load_agent()
    script = iter(
        [
            "TOOL: nope\nARG: anything",
            "ANSWER: gave up",
        ]
    )
    backend = MockChatBackend(responder=lambda s, m: next(script))
    trace = agent.run_agent(backend, "test")
    tool_step = next(s for s in trace.steps if s.kind == "tool")
    assert tool_step.result and "no such tool" in tool_step.result


def test_agent_stops_at_max_steps():
    agent = _load_agent()
    # Backend that keeps requesting tools forever.
    backend = MockChatBackend(responder=lambda s, m: "TOOL: calculate\nARG: 1 + 1")
    trace = agent.run_agent(backend, "loop?", max_steps=3)
    # 3 tool steps, then loop exits and final_answer falls back.
    assert len(trace.steps) == 3
    assert trace.final_answer is not None
