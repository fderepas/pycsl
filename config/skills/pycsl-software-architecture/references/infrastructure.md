---
name: pycsl-infrastructure
description: Infrastructure reference for the PyCSL repository. Covers bin/ shell scripts, test-suite/ structure and baseline, src/skill2rag/ RAG indexer, data/ stubs, config/skills/ layout, and ir_schema.py. Use when running tests, adding test cases, updating skills, or understanding directory conventions.
---

# PyCSL Infrastructure

---

## `bin/` — shell scripts

| Script | Purpose |
|--------|---------|
| `bin/run-reference-tests.sh` | Runs all `test-suite/corpus/pycsl-reference/` tests. Flags: `--stop-at N` (stop after test N), `--pycsl` (use installed pycsl binary). Exit 0 = all pass. |
| `bin/run-annotated.sh` | Runs `pycsl` on all files in `tests/annotated/`. |
| `bin/annotate.sh` | Entry point for annotation pipeline — calls coordinator or `agent-annotate.py` directly. |
| `bin/run-rocq-proofs.sh` | Generates Rocq/Coq proof obligations from Why3 unproven goals and calls `coqc`. |
| `bin/update-rag.sh` | Re-indexes `config/skills/` into the Chroma vector store via `src/skill2rag/`. Run after adding or editing skill files. |
| `bin/check-annotation-quality.py` | Scores annotation quality across a directory of annotated files. |
| `bin/get-meta-info.sh` | Collects meta-observability metrics from the log directory. |
| `bin/run` | Convenience wrapper — runs `pycsl` on a single file. |

### Running the reference test suite

```bash
# From the pycsl project root:
cd /path/to/pycsl

# Run all reference tests (uses venv pycsl):
bin/run-reference-tests.sh --pycsl

# Stop after test 0050 (useful during development):
bin/run-reference-tests.sh --pycsl --stop-at 50
```

Current baseline: **216/243** tests passing.

---

## `test-suite/corpus/` — test corpus

### `pycsl-reference/`

Each test is a numbered subdirectory `NNNN/` containing:

```
NNNN/
  input.py        ← annotated Python source (with #@ contracts)
  expected.mlw    ← expected WhyML output (exact string match)
  header          ← optional: CLI flags passed to pycsl
                    (e.g., --memory-model typed, --prover alt-ergo)
```

The test runner diffs `pycsl input.py` output against `expected.mlw`. Any difference is a failure.

### `negative/`

Tests where `pycsl` must exit with a non-zero status (invalid input, parse error, semantic error). Each test has an `input.py` and an optional `expected_error` pattern.

### Adding a reference test

1. Choose the next available number `NNNN`.
2. Create `test-suite/corpus/pycsl-reference/NNNN/input.py` — a correctly annotated Python file.
3. Run `pycsl input.py` and capture its output to `expected.mlw`.
4. Add a `header` file only if non-default flags are needed.
5. Run `bin/run-reference-tests.sh --pycsl --stop-at NNNN` to verify the new test passes.

---

## `src/skill2rag/` — RAG skill indexer

Indexes all markdown files under `config/skills/` into a Chroma vector store. Agents query it at runtime via `retrieve_skill_chunks()` in `common.py`.

**Embedding model:** `nomic-embed-text` via Ollama (configurable with `EMBEDDING_MODEL` env var).

**When to re-index:** after adding or significantly editing any skill file under `config/skills/`.

```bash
bin/update-rag.sh
# or directly:
python3 src/skill2rag/cli.py
```

**How retrieval works in agents:**
```python
from common import retrieve_skill_chunks, load_config

config = load_config(config_path)
chunks = retrieve_skill_chunks(
    queries=config["skill_queries"][AGENT_NAME],
    config_path=config_path
)
skill_context = "\n\n".join(chunks)
```

---

## `data/` — stubs and standard library data

### `data/why3stdlib/`

Why3 standard library theory files (`.mlw`) used by Module6 via `use` declarations. Module6 generates the appropriate `use` lines based on which operations appear in the IR.

### `src/pycsl_lib/`

Lightweight Python stub files for common library modules (`argparse`, `ast`, `json`, `numpy`, `pytest`, etc.). These are provided alongside user code when the IR pipeline needs to resolve imports from standard library modules that are not part of the user's annotated file.

Each stub defines only the classes and functions referenced in typical usage — enough to satisfy the IR emitter's import resolution without running the actual library.

---

## `config/skills/` — skill files

Skills are markdown files with YAML frontmatter (`name`, `description`) consumed by agents via RAG. Directory layout:

| Directory | Purpose |
|-----------|---------|
| `pycsl-annotate/` | Annotation skill (forbidden expressions, annotation rules) |
| `pycsl-how-to-develop/` | Developer guide for extending PyCSL |
| `pycsl-software-architecture/` | This skill — architecture reference |
| `contract-writer/` | Skill for `agent-contract-writer.py` |
| `english-writer/` | Skill for `agent-english-writer.py` |
| `invariant-writer/` | Skill for `agent-invariant-writer.py` |
| `refactor-python/` | General Python refactoring best practices |
| `rocq-prover/` | Rocq/Coq proof writing skill |

Each skill directory may have a `references/` subdirectory with more detailed reference documents linked from the main `SKILL.md`.

---

## `ir_schema.py` (`src/pycsl/ir_schema.py`)

Defines the structural contract for the JSON IR.

```python
def validate_ir(ir: dict) -> None:
    """Raise PyCSLIRError if required top-level or per-function keys are missing."""
```

Required top-level keys: `module_name`, `functions`.

Required per-function keys: `name`, `params`, `return_type`, `body`, `requires`, `ensures`.

Called by Module5 before `json.dumps()`, and by `schema_validator.py` in the agent pipeline for early validation with a user-friendly error message.

---

## `src/pycsl/__init__.py`

Empty. The package is installed with `pip install -e .` (editable mode). The `pycsl` CLI entry point is declared in `pyproject.toml`.

---

## Useful grep patterns for navigation

```bash
# Find all #@ annotation patterns in a file:
grep -n '#@' path/to/file.py

# Find all god methods (>100 lines) in the pipeline:
python3 -c "
import ast, pathlib
for p in pathlib.Path('src/pycsl').rglob('*.py'):
    tree = ast.parse(p.read_text())
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end = max(getattr(x, 'end_lineno', n.lineno) for x in ast.walk(n))
            if end - n.lineno > 100:
                print(f'{p}:{n.lineno}  {n.name}  ({end - n.lineno} lines)')
"

# Find all PyCSLError raises:
grep -rn 'raise PyCSL' src/pycsl/

# Find all sys.exit calls (should only be in pycsl.py main):
grep -rn 'sys\.exit' src/pycsl/
```
