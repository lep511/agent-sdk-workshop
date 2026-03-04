# Troubleshooting

Common things that go wrong and how to fix them. Run `./workshop check` first — it catches most of these automatically.

---

## "ANTHROPIC_API_KEY is not set"

The agent can't find your key. In order of likelihood:

1. **You didn't create `.env`** — run `cp .env.example .env` and edit it
2. **You edited `.env.example` instead of `.env`** — the example file is just a template
3. **You're in the wrong directory** — `.env` loads from the repo root; if you moved it, the agents won't find it
4. **Your key has whitespace** — make sure the line is exactly `ANTHROPIC_API_KEY=sk-ant-...` with no quotes or trailing spaces

To verify: run `./workshop check`.

---

## "No module named 'claude_agent_sdk'"

You didn't install the requirements, or you installed them in a different Python environment than you're running.

```bash
# Make sure you're using the same python/pip
which python
which pip

# Reinstall
pip install -r requirements.txt
```

If you use `pyenv`, `conda`, or a virtualenv, double-check you're inside the right environment.

---

## "SyntaxError" when running agent.py

You're probably on **Python 3.9 or older**. The SDK uses `X | Y` union syntax which needs 3.10+.

Check: `python --version`

If you have multiple Python versions installed, try `python3.10`, `python3.11`, etc. explicitly.

---

## The agent hangs / is very slow

A few possibilities:

- **Normal at first run** — the first request to the API takes a few seconds to warm up. Subsequent requests are faster.
- **Stage 2 with sub-agents** — each sub-agent spawn is its own API round-trip. Two sub-agents easily adds 5–10 seconds. This is expected.
- **You have a typo in a tool name** — if a tool in `allowed_tools` doesn't match the actual tool name (wrong server prefix, spelling error), the agent may loop trying to call it. Check the console for repeated failed tool calls.
- **Network issue** — try a plain `curl https://api.anthropic.com/` to rule this out

---

## "Error: Tool 'mcp__X__Y' not found"

The model is trying to call a tool that wasn't registered. Usually means the tool name in `allowed_tools` doesn't match the MCP server key.

The naming pattern is: `mcp__{server_key}__{tool_name}` — where `server_key` is the dict key you used in `mcp_servers={...}`, not the server's internal name.

For the guided demo: the server key is `"research"` (set in `agent.py:build_options()`), so tools are `mcp__research__*`. For breakouts: the server key matches the category name (`"support"` → `mcp__support__*`).

---

## "memory_store.json: Permission denied"

The memory system writes to a file in the same directory as the code. If you cloned into a read-only location, this won't work.

Quick fix: `chmod -R u+w .` in the repo root.

---

## "No news found for 'Apple'" / "No customer data available"

The mock tools only know about the **fictional** companies/customers/services in the data files. They don't know real companies.

- Guided demo companies: Tinplate Merchant Systems, Bucklefern Commerce Holdings, Ironvane Freight Systems
- Each breakout has its own data — check `data/*.json` for what's available

The error messages list what *is* known, so the agent will usually self-correct.

---

## Colors look like garbage (`\033[96m` literals in output)

Your terminal doesn't support ANSI colors, or you're piping output to a file.

Set `NO_COLOR=1` before running:

```bash
NO_COLOR=1 ./workshop demo
```

---

## The agent isn't using its tools / sub-agents

Even with tools enabled, the model *decides* whether to use them. A few reasons it might not:

- **Your prompt doesn't require them** — "say hi" doesn't need tools. Ask something that requires looking things up.
- **The system prompt doesn't encourage tool use** — the starter prompts nudge toward tools. If you rewrote the prompt, you may have dropped that nudge.
- **Sub-agents specifically:** the model needs to be told to delegate. The shared runner adds a "you can delegate to these sub-agents" suffix automatically, but if you overrode the system prompt assembly, that might be missing.

Try being explicit in your request: "Use your research tools to find..." or "Delegate the research to the researcher sub-agent."

---

## I changed config.py but nothing changed

You have to **restart the agent** between config changes. The config is loaded once at startup — it's not hot-reloaded.

Ctrl-C to exit, re-run `./workshop demo`.

---

## Everything works but the output quality is bad

This is the fun part — welcome to prompt engineering. See the "What to tinker with" sections in each breakout's README for specific suggestions.

General advice: be more specific in the system prompt. "Be helpful" is too vague. "When given a ticket, first look up the customer, then search the KB, then draft a response" is actionable.
