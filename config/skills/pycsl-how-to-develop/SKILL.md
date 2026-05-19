---
name: pycsl-how-to-develop
description: Developer guide for the PyCSL formal verification pipeline. Covers the project directory layout, the role of every utility in bin/, the Module1–Module6 pipeline, the agent architecture, the skills and RAG system, the test suite structure, and a step-by-step checklist for adding a new feature. Use this skill whenever scaffolding, extending, or debugging the PyCSL project.
---

# PyCSL — Developer How-To Guide

## 1. Project Directory Layout

```text
PyCSL/
├── bin/                        ← Launcher scripts and utilities
├── config/
│   ├── agents-config.json      ← Model name, project-directory, allowed tools
│   ├── schemas/                ← JSON schemas for agent I/O
│   └── skills/                 ← Skill files consumed by agents (source of truth)
│       ├── pycsl-annotate/     ← Master annotation skill
│       ├── contract-writer/    ← Contract-writing sub-agent skill
│       ├── english-writer/     ← English description sub-agent skill
│       ├── invariant-writer/   ← Loop/class invariant sub-agent skill
│       ├── polish-skill/       ← Post-processing polish rules
│       ├── agent-project-structure/  ← Canonical project layout
│       └── pycsl-how-to-develop/     ← This skill
├── src/
│   ├── pycsl/                  ← Core pipeline (Python package)
│   │   ├── Module1_Ingestor.py       ← Reads .py, strips #@ lines
│   │   ├── Module2_Parser.py         ← EBNF grammar → AST for contracts
│   │   ├── Module3_Weaver.py         ← Attaches contracts to Python AST nodes
│   │   ├── Module4_SemanticAnalyzer.py  ← Type checking, scope analysis
│   │   ├── Module5_IREmitter.py      ← Emits intermediate representation
│   │   ├── Module6_WhyMLTranspiler.py   ← Generates WhyML for Why3/Alt-Ergo
│   │   ├── pycsl.py                  ← CLI entry point
│   │   └── agents/                   ← All agent scripts
│   │       ├── coordinator.py              ← Orchestrator (retry loop)
│   │       ├── agent-annotate.py           ← Adds contracts to Python code
│   │       ├── agent-splitter.py           ← Splits file → per-function annotation
│   │       ├── agent-writer.py             ← 3-agent writer coordinator
│   │       ├── agent-english-writer.py     ← Writes English spec for a function
│   │       ├── agent-contract-writer.py    ← Writes requires/ensures/assigns
│   │       ├── agent-invariant-writer.py   ← Writes loop invariants & variants
│   │       ├── agent-reconcile.py          ← Diagnoses proof failures
│   │       ├── agent-script-update.py      ← Applies reconciliation recommendations
│   │       ├── agent-script-update-mcp.py  ← MCP server for safe updates
│   │       ├── agent-meta-evaluator.py     ← QA judge per attempt
│   │       ├── agent-meta-monitor.py       ← Operational health watchdog
│   │       ├── agent-meta-reviewer.py      ← Human-readable report generator
│   │       ├── llm_client.py              ← LLM abstraction (Ollama, API)
│   │       └── schema_validator.py        ← Validates agent I/O against schemas
│   └── skill2rag/              ← Skill → RAG compiler (chunk, embed, index)
├── data/
│   ├── embeddings/             ← Generated RAG index (skills_index.json)
│   └── lib_stubs/              ← Library stub files with trusted contracts
├── tests/
│   ├── to_annotate/            ← Input Python scripts (001–069+)
│   └── annotated/              ← Output annotated scripts (auto-generated)
├── test-suite/
│   ├── annotations.md          ← Authoritative annotation reference (NEVER renumber)
│   ├── traceability-pycsl.md   ← Ref → Test ID mapping
│   ├── corpus/
│   │   ├── pycsl-reference/    ← Reference test files (0001–0190+)
│   │   ├── imported/           ← Multi-file import tests
│   │   ├── edge_cases/         ← Edge-case tests
│   │   └── negative/           ← Expected-failure tests
│   ├── library_reference/      ← English specs for standard library modules
│   ├── runner/                 ← Static/dynamic oracle, evaluator, reporter
│   ├── instrumenter/           ← CSL-to-Python contract instrumenter
│   └── run_suite.py            ← Dual-oracle test runner
├── metrics/                    ← Runtime logs and meta-agent outputs
│   ├── logs/                   ← stdout/stderr per attempt
│   ├── evaluator/              ← QA evaluation JSON per attempt
│   ├── monitor/                ← Operational health JSON per file
│   └── reviewer/               ← Human-readable reports
└── pyproject.toml              ← Python project metadata
```

## 2. Utilities in `bin/`

| Script | Purpose |
|--------|---------|
| `run.sh` | **Main entry point.** Runs the full coordinator pipeline: annotate → prove → reconcile → update. Accepts `--start-at N` to skip files before number N. |
| `annotate.sh` | Annotate a single file without proof or reconciliation. |
| `run-annotated.sh` | Run `pycsl` on all files in `tests/annotated/` (manual validation). |
| `check-annotation-quality.py` | Analyze annotation quality: reports trivial contracts, missing assigns, etc. |
| `get-meta-info.sh` | Query meta-agent outputs (evaluator, monitor, reviewer) for a given file stem. |
| `update-rag.sh` | Rebuild the RAG index from all skills in `config/skills/`. **Must be run after any skill update.** |
| `run-reference-tests.sh` | Run all tests in `test-suite/corpus/pycsl-reference/`. Supports `# pycsl-flags:` and `# pycsl-expected: FAIL` directives in test files. Common flags: `--no-proof` (skip prover), `--fun NAME` (verify one function), `--deep` (transitive imports). |

## 3. Pipeline Architecture

```text
Python file (.py)
    │
    ▼
Module1_Ingestor    ← reads file, separates code from #@ annotations
    │
    ▼
Module2_Parser      ← parses #@ lines using EBNF grammar → contract AST
    │
    ▼
Module3_Weaver      ← attaches contract AST nodes to Python AST nodes
    │
    ▼
Module4_SemanticAnalyzer  ← type/scope checking, variable resolution, protected-access checks
    │
    ▼
ConcurrencyChecker  ← (warnings only) static concurrency analysis; recognises trusted types
    │
    ▼
Module5_IREmitter   ← emits intermediate representation (functions, classes, invariants, shared state)
    │
    ▼
Module6_WhyMLTranspiler   ← generates .mlw (WhyML) file
    │
    ▼
Why3 / Alt-Ergo     ← SMT solver proves or rejects the goals
```

### CLI Flags (`pycsl.py`)

| Flag | Effect |
|------|--------|
| `--no-proof` | Skip Why3 prover invocation. Reports SUCCESS if valid WhyML is generated without errors. Useful for testing transpiler output without requiring provable postconditions. |
| `--keep-mlw` | Keep the generated `.mlw` file next to the input (instead of a temp file). |
| `--fun NAME` | Only verify the named function (and transitive call-deps). May be repeated. |
| `--deep` | Recursively resolve transitive imports in dependency files. |
| `--rocq DIR` | On SMT failure, generate Rocq proof skeletons in DIR. |
| `--rocq-proofs [DIR]` | Replay pre-existing Rocq proofs from DIR (auto-detects `<file>.proofs/`). |
| `-p PROVER` | Use a specific prover (e.g., `Alt-Ergo,2.6.2,`). |
| `--memory-model M` | Memory model: `hoare` (default), `typed`, `store`, or `concurrent`. |

### CLI Flags (`agent-annotate.py`)

| Flag | Effect |
|------|--------|
| `--in FILE` | Input Python source file to annotate. |
| `--out FILE` | Output path for annotated file. |
| `--trusted` | Progressive verification: run full LLM pipeline for real contracts, mark all functions `#@ \trusted`, then prove bottom-up (leaves first) and remove `\trusted` from each function that passes `pycsl --no-proof`. Functions that cannot be verified keep `\trusted` as temporary scaffolding. |

## 4. Agent Architecture

### Annotation Pipeline (per file)

```text
agent-splitter.py
    ├── Step 1: Extract functions, build call graph
    ├── Step 2: Filter annotatable (skip __dunder__, @property)
    ├── Step 2b: Generate class invariants (calls writer with __init__)
    ├── Step 3: Detect SCCs, topological order
    ├── Step 4: Annotate each function via agent-writer.py
    │       └── agent-writer.py (3-agent pipeline)
    │           ├── agent-english-writer.py  → English specification
    │           ├── agent-contract-writer.py → requires / ensures / assigns
    │           └── agent-invariant-writer.py → loop invariants, variants
    └── Step 5: Reassemble file (insert invariants + annotated methods)
```

### Coordinator Loop (per file, up to 10 retries)

```text
coordinator.py
    ├── agent-annotate.py       → produces annotated .py in tests/annotated/
    ├── pycsl (proof)           → exit 0 = pass, exit 1 = fail
    │   (if fail)
    ├── agent-reconcile.py      → diagnosis + recommendation JSON
    ├── agent-script-update.py  → applies fix via MCP
    ├── agent-meta-evaluator.py → QA re-check
    └── (retry)
```

### Meta-Agents (post-hoc)

- **agent-meta-monitor.py** — parses all attempt logs → operational health JSON
- **agent-meta-reviewer.py** — generates human-readable PR description

## 5. Skills and RAG System

### Skill Files

Each skill lives in `config/skills/<name>/SKILL.md` with YAML frontmatter:

```yaml
---
name: pycsl-annotate
description: Master annotation skill for the PyCSL agent pipeline...
---
```

The body contains rules, examples, and NEVER constraints that the LLM agents follow.

### RAG Compilation

Skills are compiled into a vector index by `src/skill2rag/`:

```bash
./bin/update-rag.sh
# or equivalently:
python src/skill2rag build --skill-dir config/skills
```

This produces `data/embeddings/skills_index.json` (chunked text + 768-dimensional vectors via Ollama). Agents query this index at runtime to retrieve relevant skill fragments.

**CRITICAL: Run `./bin/update-rag.sh` after ANY change to a skill file.**

### Skill Inventory

| Skill | Used By | Purpose |
|-------|---------|---------|
| `pycsl-annotate` | agent-annotate.py | Master annotation rules, NEVER constraints |
| `contract-writer` | agent-contract-writer.py | Requires/ensures/assigns generation |
| `english-writer` | agent-english-writer.py | English spec generation |
| `invariant-writer` | agent-invariant-writer.py | Loop invariant/variant generation |
| `polish-skill` | agent-annotate.py | Post-processing polish rules |
| `agent-project-structure` | project scaffolding | Directory layout conventions |
| `pycsl-how-to-develop` | developer reference | This skill |

## 6. Library Stubs

`data/lib_stubs/` contains Python files with `#@ \trusted` contracts for standard library modules. These provide specifications for functions like `math.sqrt`, `random.randint`, etc., so the prover can reason about external calls without verifying their implementations.

Convention:
- One file per module (e.g., `math_stub.py`, `random_stub.py`)
- Each function has `#@ \trusted` and a full contract
- `#@ \trusted` in stub files is permanent (these are axioms about external code)
- `#@ \trusted` in user code is temporary scaffolding (see `--trusted` flag below)

## 7. Test Suite Structure

### Reference Tests (`test-suite/corpus/pycsl-reference/`)

Numbered test files (`0001.py` – `0190.py`+) exercising specific annotation features. Each test has:

```python
"""Test 0006 — PyCSL Annotation Reference 2.3.1"""
""  # pycsl
#@ class invariant self._value >= 0
class Counter:
    ...
if __name__ == "__main__":
    c = Counter()
    assert c.increment(5) == 5
```

### Annotations Reference (`test-suite/annotations.md`)

The authoritative document listing all PyCSL annotations. Numbered sections and table rows. **NEVER change existing numbering** — only append or insert within sections.

### Traceability (`test-suite/traceability-pycsl.md`)

Maps each annotation reference item (e.g., `2.3.1`) to test IDs:

```text
| 2.3.1 | Class invariant | 0006, 0076, 0077 | PASS |
```

### Dual-Oracle Runner (`test-suite/run_suite.py`)

Runs tests through:
1. **Static oracle** — compiles to WhyML and runs Why3/Alt-Ergo
2. **Dynamic oracle** — instruments contracts as Python assertions and runs

## 8. How to Add a New Feature to PyCSL

Follow this checklist in order:

### Step 1: Update `test-suite/annotations.md`
- Add the new annotation directive or pattern to the appropriate section
- **NEVER change existing numbering** (section numbers, table row numbers)
- Append new rows to tables or add new subsections

### Step 2: Add reference tests
- Create new `.py` files in `test-suite/corpus/pycsl-reference/`
- Use the next available number (e.g., `0191.py`, `0192.py`)
- Follow the docstring convention: `"""Test NNNN — PyCSL Annotation Reference X.Y.Z"""`
- Include an `if __name__ == "__main__":` block with `assert` statements

### Step 3: Update `test-suite/traceability-pycsl.md`
- Add a row mapping the annotation reference to the new test IDs
- Format: `| Ref | Section Title | Test IDs | Status |`

### Step 4: Implement the feature
- **Parser**: Update EBNF grammar in `Module2_Parser.py`
- **Weaver**: Update `Module3_Weaver.py` to attach new AST nodes
- **IR**: Update `Module5_IREmitter.py` to emit the new construct
- **WhyML**: Update `Module6_WhyMLTranspiler.py` to generate the WhyML output
- **bin/ scripts**: If the feature adds or changes a script in `bin/`, update `README.md` (Usage section) — `bin/` scripts are user-facing tools and the README is the primary human documentation

### Step 5: Update skill files

**ALL FIVE skills listed below must be reviewed on every new feature.** Each skill
feeds a different LLM agent; an agent that does not know about a new feature will
silently produce wrong output that fails at proof time.

| Skill file | Agent that uses it | Update when… |
|---|---|---|
| `config/skills/pycsl-annotate/SKILL.md` | `agent-annotate`, `agent-writer` (fallback) | Any new annotation, grammar rule, forbidden pattern, or memory model |
| `config/skills/contract-writer/SKILL.md` | `agent-contract-writer` | New `requires`/`ensures`/`assigns` atoms, new memory model, new function-level annotations (`\diverges`, `\trusted`, `thread_entry`, etc.) |
| `config/skills/invariant-writer/SKILL.md` | `agent-invariant-writer` | New loop/class invariant constructs, new memory model loop rules, new control-flow annotations (`continue`, `diverges`) |
| `config/skills/english-writer/SKILL.md` | `agent-english-writer` | Changes that affect how functions should be described in English (new constructs that require specific phrasing) |
| `config/skills/pycsl-how-to-develop/SKILL.md` | developer reference | Any process change, new pipeline step, new memory model, new agent |

**Checklist — do not close a feature branch until all five rows are checked:**

```
[ ] pycsl-annotate/SKILL.md  — master skill updated
[ ] contract-writer/SKILL.md — new memory-model section or new atoms added
[ ] invariant-writer/SKILL.md — new memory-model loop rules added
[ ] english-writer/SKILL.md  — English description guidance updated if needed
[ ] pycsl-how-to-develop/SKILL.md — this file updated if process changed
```

**Why this matters:** agents rely on RAG-indexed skills at runtime, not on
`annotations.md` or source code. A skill that is one feature behind will produce
annotations that fail at Module4 semantic analysis or at the Why3 proof step —
often with an error that is hard to diagnose as a skill gap rather than a code bug.

**Historical example (concurrent model, 2026-05):** `pycsl-annotate/SKILL.md` was
updated with the full concurrent-model section (Section 6) but `contract-writer/SKILL.md`
and `invariant-writer/SKILL.md` were not updated. This caused `agent-contract-writer`
to write `requires`/`ensures` clauses referencing shared variables directly (which
Module4 rejects), and `agent-invariant-writer` to add loop variants to outer
`while True:` loops in thread entry functions (which breaks the proof).

### Step 6: Rebuild RAG
```bash
./bin/update-rag.sh
```

### Step 7: Add integration tests
- Add to-annotate test files in `tests/to_annotate/`
- Run the full pipeline:
```bash
./bin/run.sh
```

### Step 8: Validate
- Check annotated output in `tests/annotated/`
- Verify proof passes (exit code 0 from pycsl)
- Review meta-agent outputs in `metrics/`

## 9. Configuration

### `config/agents-config.json`
Contains model name, project directory path, and allowed tools for agent execution.

### `config/schemas/`
JSON schemas validating agent input/output formats (reconciliation recommendations, meta-agent reports).

### Environment
- Python virtual environment expected at `.venv/`
- `pycsl` binary must be on PATH
- Ollama must be running locally for RAG embedding generation
