# Agent SDK Workshop

Hands-on workshop materials for building production agents with the [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python).

**No code writing required.** You flip switches, pick from component lists, and write prompts. The SDK does the rest.

---

## Quick start

```bash
# 1. Clone and enter
git clone <repo-url> agent-sdk-workshop
cd agent-sdk-workshop

# 2. Install (Python 3.10+)
pip install -r requirements.txt

# 3. Set your API key
cp .env.example .env
# → edit .env and paste your key after ANTHROPIC_API_KEY=

# 4. Verify everything works
./workshop check
#   (on Windows: python workshop check)

# 5. Run the first exercise
./workshop demo
```

---

## Structure

```
01-guided-demo/    One agent, four stages. Flip switches in config.py, re-run, watch it improve.
02-breakouts/      Pick a use case. Assemble an agent from pre-built tools and sub-agents.
extend/            Finished early? Recipes for adding your own tools, sub-agents, and breakouts.
docs/              Cheat sheet, FAQ, troubleshooting.
```

---

## The `./workshop` command

One entry point for everything:

| Command | Does |
|---|---|
| `./workshop check` | Verify your setup before starting (Python version, API key, SDK) |
| `./workshop demo` | Run the guided demo agent |
| `./workshop demo --show-prompt` | See the full context the SDK is sending to the model |
| `./workshop breakout` | List available breakouts |
| `./workshop breakout <name>` | Run a specific breakout |
| `./workshop reset` | Clear all memory files (fresh start) |

On Windows, prefix with `python`: `python workshop check`.

---

## Part 1 — Guided demo

**One agent. One task. Four runs.** Between each run, flip one switch in `config.py` and watch the agent get better at the same job.

| Stage | Toggle | SDK primitive | What unlocks |
|---|---|---|---|
| 0 | *(all off)* | `system_prompt` | Just chat — no tools, no state |
| 1 | `ENABLE_TOOLS` | `@tool` + `mcp_servers` | Agent can look things up |
| 2 | `ENABLE_SUBAGENTS` | `AgentDefinition` + `Task` tool | Agent delegates to specialists |
| 3 | `ENABLE_MEMORY` | `hooks` + a persistence tool | Agent remembers across restarts |

→ Open [`01-guided-demo/GUIDE.md`](./01-guided-demo/GUIDE.md) for the stage-by-stage walkthrough.

---

## Part 2 — Breakouts

**Pick a use case. Assemble an agent.** You get a library of pre-built tools (6 categories, 19 tools) and 6 sub-agents. Each breakout's `config.py` is where you pick which to enable and write the system prompt.

| Breakout | Scenario |
|---|---|
| `00-warmup` | Same briefing task from the demo, but assembled the breakout way |
| `chief-of-staff` | Board meeting prep, email drafting, exec briefings |
| `customer-support` | Ticket triage with KB-grounded responses |
| `sre-agent` | Incident investigation — correlate deploys, metrics, runbooks |
| `account-intelligence` | Pre-renewal account review — surface hidden churn risks |
| `freeform` | Blank canvas — you have your own use case |

→ Open [`02-breakouts/README.md`](./02-breakouts/README.md) to pick one.

---

## Requirements

- **Python 3.10+** (the SDK uses modern type syntax)
- **An Anthropic API key**
- That's it. Every tool is backed by local mock data — no external services, no extra credentials.

---

## If something breaks

1. Run `./workshop check` — catches most setup issues
2. Check [`docs/TROUBLESHOOTING.md`](./docs/TROUBLESHOOTING.md)
3. Check [`docs/FAQ.md`](./docs/FAQ.md)

---

## Going further

- [`extend/`](./extend/) — recipes for adding your own tools, sub-agents, and breakouts
- [`docs/CHEATSHEET.md`](./docs/CHEATSHEET.md) — every SDK pattern on one page
- [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python) — the SDK itself, with more examples
- [claude-cookbooks / claude_agent_sdk](https://github.com/anthropics/claude-cookbooks/tree/main/claude_agent_sdk) — deeper reference agents
