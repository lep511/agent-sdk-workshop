# Extend — Go Further

Finished early? Want to keep building after the workshop? This directory has recipes for extending the repo with your own components.

Everything here builds on what you learned in the guided demo and breakouts — no new concepts, just applying the patterns you've already seen.

---

## Recipes

| What you want to do | Start here |
|---|---|
| Add a new tool to the shared library | [`add-a-tool.md`](./add-a-tool.md) |
| Add a new sub-agent to the shared library | [`add-a-subagent.md`](./add-a-subagent.md) |
| Create a sixth breakout for your own use case | [`add-a-breakout.md`](./add-a-breakout.md) |
| Swap mock JSON for a real API call | [`connect-a-real-api.md`](./connect-a-real-api.md) |
| Get machine-readable JSON output instead of prose | [`structured-output.md`](./structured-output.md) |
| Get ideas for what to build | [`ideas.md`](./ideas.md) |

---

## Quick start: new breakout in 5 minutes

```bash
cp -r extend/_template 02-breakouts/my-agent
# Edit 02-breakouts/my-agent/config.py — pick tools, write a prompt
# Drop some JSON in 02-breakouts/my-agent/data/
./workshop breakout my-agent
```

See [`add-a-breakout.md`](./add-a-breakout.md) for the detailed version.

---

## Reference cards

Keep [`../docs/CHEATSHEET.md`](../docs/CHEATSHEET.md) open — every SDK pattern on one page.
