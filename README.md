# PyCSL — Self-Healing Formal Verification Pipeline

PyCSL is an agentic pipeline that takes Python scripts, annotates them with
Hoare-logic contracts using an LLM, verifies the annotations with the
[Why3](https://why3.lri.fr/) / Alt-Ergo proof engine, and automatically
repairs failures through a reconcile → update agent loop.

---

## Directory layout

```
PyCSL/
├── pycsl                   # Proof runner (calls Why3/Alt-Ergo)
├── run.sh                  # Main entry point (see Usage below)
├── tests/
│   ├── to_annotate/        # Input Python scripts (unannotated)
│   └── annotated/          # Auto-generated annotated scripts
├── metrics/                # Meta-agent outputs (created at runtime)
│   ├── logs/               # Captured stdout/stderr per attempt
│   ├── evaluator/          # Per-attempt QA evaluation JSON
│   ├── monitor/            # Per-file operational health JSON
│   └── reviewer/           # Human-readable report (JSON + Markdown)
└── agents/
    ├── coordinator.py          # Orchestrator — owns the full retry loop
    ├── agent-annotate.py       # Adds Hoare-logic contracts to a Python file
    ├── agent-reconcile.py      # Diagnoses pycsl failures → recommendation JSON
    ├── agent-script-update.py  # Applies recommendations to agent-annotate.py
    │                           #   or skill-annotate.md (never tests/annotated/)
    ├── agent-script-update-mcp.py  # MCP server enforcing write restrictions
    ├── agent-meta-evaluator.py # QA judge: syntax + pycsl re-check after each fix
    ├── agent-meta-monitor.py   # Operational watchdog: JSON failures, MCP rejections
    ├── agent-meta-reviewer.py  # LLM-generated PR description + system recommendation
    ├── skill-annotate.md       # Annotator skill/prompt (editable by update agent)
    └── agents-config.json      # Shared config (model, project-directory, …)
```

---

## How it works

```
For each .py file in tests/to_annotate/:

  ┌─────────────┐
  │ agent-      │  adds @requires / @ensures / @invariant / @variant
  │ annotate.py │  contracts to the Python script
  └──────┬──────┘
         │ annotated file → tests/annotated/
         ▼
  ┌─────────────┐
  │   pycsl     │  compiles to WhyML and runs Alt-Ergo
  └──────┬──────┘
         │ pass → next file
         │ fail ──────────────────────────────────────────────┐
         ▼                                                    │
  ┌──────────────────┐                                        │
  │ agent-reconcile  │  reads pycsl output + annotated file   │
  │ .py              │  → recommendation JSON                 │
  └──────┬───────────┘                                        │
         │                                                    │
         ▼                                                    │
  ┌──────────────────────┐                                    │
  │ agent-script-update  │  edits agent-annotate.py or        │
  │ .py                  │  skill-annotate.md via MCP         │
  └──────┬───────────────┘                                    │
         │                                                    │
         ▼                                                    │
  ┌──────────────────────┐                                    │
  │ agent-meta-evaluator │  syntax check + pycsl re-run       │
  └──────────────────────┘                                    │
         │                                                    │
         └────────────────── retry (max 10) ─────────────────┘

  After all retries for a file:
  ┌──────────────────────┐
  │ agent-meta-monitor   │  parse all attempt logs → health JSON
  └──────────────────────┘

  On halt (exit 72 or 73):
  ┌──────────────────────┐
  │ agent-meta-reviewer  │  LLM-generated PR body + recommendation
  └──────────────────────┘
```

### Loop detection

If `agent-reconcile` produces the **same recommendation 3 times in a row**
the coordinator halts with **exit code 73** so a human can intervene.
A report is automatically written to `metrics/reviewer/`.

### Exit codes

| Code | Meaning |
|------|---------|
| `0`  | All files passed |
| `1`  | Generic error |
| `72` | Max retries (10) exhausted for at least one file |
| `73` | Loop detected — identical recommendation 3× in a row |

---

## Usage

### Full pipeline (annotate → prove → repair loop)

```bash
./run.sh
```

### Re-run a meta-agent on existing metrics (without re-annotating)

```bash
# Re-generate the reviewer report for a file
./run.sh --review 001-basic-control-flow

# Re-run the operational health monitor for a file
./run.sh --monitor 001-basic-control-flow

# Re-run the QA evaluator for a specific annotated/modified file pair
./run.sh --evaluate 001-basic-control-flow \
    tests/annotated/001-basic-control-flow.py \
    agents/skill-annotate.md
```

The `<file-stem>` argument is the filename without extension, matching what
is stored under `metrics/`.

### Output locations

| Meta-agent | Output |
|------------|--------|
| `agent-meta-evaluator` | `metrics/evaluator/<stem>_<attempt>.json` |
| `agent-meta-monitor`   | `metrics/monitor/<stem>.json` |
| `agent-meta-reviewer`  | `metrics/reviewer/<stem>.json` + `<stem>.md` |

---

## Configuration

Edit `agents/agents-config.json` to change the LLM model or project directory:

```json
{
  "model": "claude-sonnet-4.6",
  "project-directory": "./my_project",
  "skill-annotate": "skill-annotate.md"
}
```

The update agent may only modify `agents/agent-annotate.py` or
`agents/skill-annotate.md` — writing to `tests/annotated/` is blocked by the
MCP server.
