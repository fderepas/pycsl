---
name: pycsl-agent-pipeline
description: Full description of the PyCSL LLM agent orchestration layer. Covers the coordinator workflow, agent-annotate GuardPipeline, agent-splitter Tarjan SCC, the three writer agents, agent-reconcile, agent-script-update, meta-agents, and supporting modules. Use when adding, modifying, or debugging agents in src/pycsl/agents/.
---

# PyCSL Agent Pipeline

The agent layer sits above the compiler pipeline. Its job: take a plain Python file and produce a correctly-annotated version that `pycsl` can verify. The flow is iterative — annotate → prove → fix → repeat.

---

## Coordinator (`coordinator.py`, class `CoordinatorAgent`)

**Entry point for the automated annotation and proof loop.**

Constructor: `CoordinatorAgent(pycsl_dir: Path)`

Key attributes set in `__init__`:
- `self.pycsl_dir` — project root
- `self.agents_dir` — `src/pycsl/agents/`
- `self.to_annotate_dir` — `tests/to_annotate/`
- `self.annotated_dir` — `tests/annotated/`
- `self.pycsl_bin` — located via `.venv/bin/pycsl` > `PATH` > `src/pycsl/pycsl.py`

**Workflow per file:**
1. Clean `tests/annotated/` for the target file.
2. Call `agent-annotate.py` to produce an annotated version.
3. Run `pycsl` on the annotated file.
4. On failure: call `agent-reconcile.py` → get a fix recommendation.
5. Apply the recommendation via `agent-script-update.py`.
6. Loop from step 3 (up to `MAX_RETRIES`).
7. After each fix: call `agent-meta-evaluator.py`.
8. After all retries for a file: call `agent-meta-monitor.py`.
9. On halt (exit 72/73): call `agent-meta-reviewer.py`.

**Exit codes:**
- `0` — all files verified successfully
- `72` (EXIT_MAX_RETRIES) — retries exhausted, pycsl still failing
- `73` (EXIT_LOOP_DETECTED) — same reconcile recommendation 3× in a row — human intervention needed

---

## agent-annotate.py

**Purpose:** reads a Python source file and produces a version with `#@` contract comments that `pycsl` can accept.

**`AGENT_NAME = "agent-annotate"`**

### GuardPipeline

```python
class GuardPipeline:
    def __init__(self, code: str) -> None: ...
    def apply(self, name: str, transform: Callable[[str], str]) -> GuardPipeline: ...
    # .code holds the current state; ._log records which guards ran
```

Transforms are applied as a chain: each is `str → str` and must be idempotent. Errors inside a guard are logged but do not stop the pipeline. Guards run in registration order.

**Pre-LLM guards** (fix the input before sending to the LLM):
- `_strip_default_args` — removes default argument values that confuse the LLM
- `_ensure_function_contracts` — adds stub `#@ requires True` when a function has no contracts

**Post-LLM guards** (fix the LLM output):
| Guard | What it fixes |
|-------|--------------|
| `_annotate_trusted` | Wraps functions with unsupported constructs in `#@ \trusted` |
| `_prove_and_strip` | Runs pycsl and strips contracts that cause Why3 failures |
| `_inject_recursive_variants` | Adds missing loop/recursive variants |
| `_fix_list_return_type` | Fixes `list` return type annotations to `array int` |
| `_guard_list_params` | Rewrites `list` parameter types to `array int` |
| `_guard_str_params_rewrite` | Rewrites `str` parameters (unsupported by Why3) |
| `_guard_bool_constants_in_contracts` | Replaces `True`/`False` with `true`/`false` |
| `_guard_floordiv_in_contracts` | Replaces `//` with `div` in contract expressions |
| `_guard_str_length_neutralize` | Neutralizes `len(str_param)` in contracts |
| `_check_class_invariant_guards` | Adds class invariant stubs |
| `_dedup_contract_blocks` | Removes duplicate `#@` blocks on the same function |
| `_fix_empty_conditional_bodies` | Adds `pass` to empty `if`/`else` branches |
| `_strip_external_type_bodies` | Strips bodies of external library classes |

**Compiled regex constants** (module-level, `_RE_` prefix):
- `_RE_ANN` — matches any `#@` annotation line (with optional leading whitespace)
- `_RE_TRUSTED` — matches `#@ \trusted` lines
- `_RE_DEF` — captures `(indent, func_name)` from `def` lines
- `_RE_DEF_PARAMS` — captures `(indent, params)` from `def` lines
- `_RE_LIST_PARAM` — finds `param: list` parameter type hints
- `_RE_STR_PARAM` — finds `param: str` parameter type hints

---

## agent-splitter.py

**Purpose:** partitions a multi-function annotated file into strongly-connected components (SCCs) so that functions can be verified in dependency order.

Uses Tarjan's SCC algorithm on the call graph. Each SCC is a group of mutually recursive functions. The splitter outputs groups in topological order so `pycsl` proves leaf functions first.

---

## agent-writer.py (three sub-writers)

Orchestrates three specialised agents, each producing a different part of the annotation:

| Agent | File | Output |
|-------|------|--------|
| English writer | `agent-english-writer.py` | Plain-English pre/postcondition descriptions (comments) |
| Contract writer | `agent-contract-writer.py` | Formal `#@ requires`/`#@ ensures` contracts |
| Invariant writer | `agent-invariant-writer.py` | `#@ loop_invariant` and `#@ loop_variant` annotations |

The three outputs are merged by `agent-writer.py` before handing off to `pycsl`.

---

## agent-reconcile.py

**Purpose:** on `pycsl` proof failure, diagnoses the WhyML error and proposes a fix.

Input: annotated Python source + Why3 error output.
Output: a structured JSON recommendation dict with fields like `action`, `function`, `contract`, `replacement`.

The recommendation is consumed by `agent-script-update.py`.

---

## agent-script-update.py / agent-script-update-mcp.py

**Purpose:** applies a reconcile recommendation as a text patch to the annotated Python source.

`agent-script-update-mcp.py` is an alternative implementation using MCP tool calls for the patch operation.

---

## Meta-agents

Three agents provide observability over the annotation loop:

| Agent | When called | Purpose |
|-------|-------------|---------|
| `agent-meta-evaluator.py` | After each fix attempt | Scores the quality of the change (LLM judge) |
| `agent-meta-monitor.py` | After all retries for a file | Checks operational health metrics |
| `agent-meta-reviewer.py` | On coordinator halt (exit 72/73) | Writes a human-readable diagnostic report |

All three import `log` from `common` directly (not via the fragile `try/except ImportError` fallback).

---

## Supporting modules

### schema_validator.py

Wraps `validate_ir()` from `ir_schema.py`. Called by agents before passing a JSON IR to Module6 to catch structural errors early, with a friendlier error message than raw `KeyError`.

### agents-config.json (`config/agents-config.json`)

Per-agent configuration consumed at startup via `load_config()`:
- `skill_queries` — list of RAG query strings used by `retrieve_skill_chunks()`
- `model` — LLM model identifier for this agent
- `provider` — `"ollama"` or `"githubcopilot"`
- `temperature`, `max_tokens` — generation parameters

---

## Logging convention

All agents use:
```python
from common import log
log(project_dir, AGENT_NAME, f"[{AGENT_NAME}] some message\n")
```

This writes to `<project_dir>/log/<AGENT_NAME>.log` with an ISO timestamp. `print()` is reserved for user-facing CLI output only.
