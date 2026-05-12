# agent — ReAct-style tool-use starter

Bounded tool-calling loop with two built-in tools (calculator + stub search). The agent emits `TOOL:` / `ARG:` lines, the harness executes the tool, feeds the result back, repeats until `ANSWER:` or `max_steps` runs out.

```bash
pip install -e ".[anthropic,dev]"
python app.py
```

Use `run_agent(backend, question, tools=[...], max_steps=N)` to drop in your own tools; each tool is a `(name, description, fn: str -> str)` tuple.
