# agent — ReAct-style tool-use starter

Bounded tool-calling loop with two built-in tools (calculator + stub search). The agent emits `TOOL:` / `ARG:` lines, the harness executes the tool, feeds the result back, repeats until `ANSWER:` or `max_steps` runs out.

Run it in the environment where fde-starter-kit is installed (the app imports `fde_kit.backends`):

```bash
python app.py                     # MockChatBackend, no key needed
export ANTHROPIC_API_KEY=sk-ant-...
python app.py                     # real Claude; needs fde-starter-kit[anthropic]
```

Use `run_agent(backend, question, tools=[...], max_steps=N)` to drop in your own tools; each tool is a `(name, description, fn: str -> str)` tuple.
