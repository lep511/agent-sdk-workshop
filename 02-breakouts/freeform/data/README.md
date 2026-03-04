# Freeform breakout — data directory

This directory is intentionally empty. Drop JSON files here to feed the tool categories you enable.

## Expected file shapes per category

**`knowledge`** → `knowledge_base.json` and/or `documents.json`:
```json
[{"id": "...", "title": "...", "body": "...", "tags": ["..."]}]
```

**`schedule`** → `calendar.json`:
```json
[{"date": "YYYY-MM-DD", "time": "HH:MM", "title": "...", "attendees": ["..."], "notes": "..."}]
```

**`support`** → `customers.json`, `tickets.json`:
```json
// customers.json
[{"id": "C-...", "email": "...", "name": "...", "plan": "...", "status": "...", "notes": "..."}]
// tickets.json
[{"id": "T-...", "customer_id": "C-...", "subject": "...", "status": "open", "priority": "...", "thread": [{"from": "...", "at": "...", "body": "..."}]}]
```

**`ops`** → `services.json`, `alerts.json`, `runbooks.json`:
```json
// services.json
[{"name": "...", "status": "healthy|degraded|down", "dependencies": ["..."], "current_alerts": ["..."], "last_deploy": "..."}]
// alerts.json
[{"fired_at": "...", "service": "...", "severity": "info|warning|critical", "message": "..."}]
// runbooks.json
[{"id": "RB-...", "title": "...", "summary": "...", "steps": ["...", "..."]}]
```

**`code`** → point `DATA_DIR` at an actual code directory instead of here.

**`memory`** → creates `memory_store.json` automatically at runtime.

---

## Easiest path

Copy the data directory from another breakout that's close to your use case:

```bash
cp ../customer-support/data/* .
```

Then edit the JSON to match your scenario.
