# Pipeline + Agent Architecture

Load when debugging a Module1–Module6 stage, understanding the
annotation pipeline, or modifying the coordinator/retry loop.

## Pipeline Architecture

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
Why3 / Alt-Ergo     ← Why3 generates weakest-precondition VCs; Alt-Ergo (then Z3) discharges each (Valid / Unknown / Timeout)
```

### `pycsl.py` CLI Flags

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

### `agent-annotate.py` CLI Flags

| Flag | Effect |
|------|--------|
| `--in FILE` | Input Python source file to annotate. |
| `--out FILE` | Output path for annotated file. |

## Agent Architecture

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
