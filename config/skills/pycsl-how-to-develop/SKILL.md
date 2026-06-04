---
name: pycsl-how-to-develop
description: Guide developers through the PyCSL formal verification pipeline. Covers the project directory layout, the role of every utility in bin/, the Module1–Module6 pipeline, the agent architecture, the skills and RAG system, the test suite structure, and a step-by-step checklist for adding a new feature. Use this skill whenever scaffolding, extending, or debugging the PyCSL project.
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
│   │   ├── Module6_WhyMLTranspiler.py   ← Facade; JSON IR → WhyML
│   │   ├── module6_whyml/            ← Module 6 subpackage:
│   │   │   ├── ir_scanner.py         ←   Stateless IR-tree analysis
│   │   │   ├── identifiers.py        ←   whyml_ident / safe_mutex_name / OP_MAP / WHYML_RESERVED
│   │   │   ├── scc.py                ←   Tarjan SCC + call-graph for emission order
│   │   │   ├── auto_trust.py         ←   AutoTrustMixin: auto-trust + linear-VC classification
│   │   │   ├── abstract_ops.py       ←   AbstractOpsMixin: abstract-val registry
│   │   │   ├── types.py              ←   TypeInferenceMixin: RHS classification + field types
│   │   │   ├── expressions.py        ←   ExpressionEmissionMixin: _EXPR_DISPATCH targets
│   │   │   ├── statements.py         ←   StatementEmissionMixin: _handle_*_stmt + body wrap
│   │   │   ├── preamble.py           ←   PreambleEmissionMixin: use / exceptions / helpers / axioms
│   │   │   └── functions.py          ←   FunctionEmissionMixin: signature + contracts + state reset
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
├── docs/                       ← Reference docs and glossary
│   ├── glossary/               ← Human-facing vocabulary (witness, ghost code, memory model, ...)
│   ├── pycsl-concrete-syntax-reference.md
│   ├── pycsl-static-semantics-reference.md
│   └── pycsl-translational-reference.md
└── pyproject.toml              ← Python project metadata
```

---

## Reference files

Detail-heavy material lives next to this skill in `references/`.
Load on demand:

- **[`references/utilities-and-config.md`](references/utilities-and-config.md)**
  — Inventory of `bin/` scripts (run.sh, annotate.sh, update-rag.sh,
  run-reference-tests.sh, …) plus `config/agents-config.json` /
  `config/schemas/` + environment requirements. Load before invoking
  any `bin/` tool or setting up the dev environment.
- **[`references/architecture.md`](references/architecture.md)** —
  Module 1–6 pipeline diagram + `pycsl.py` and `agent-annotate.py`
  CLI flag tables + agent annotation pipeline + coordinator retry
  loop + meta-agent post-hoc tools. Load when debugging a stage or
  modifying the orchestration.
- **[`references/skills-and-rag.md`](references/skills-and-rag.md)**
  — Skill file format, the terminology-glossary convention,
  RAG-index regeneration (`./bin/update-rag.sh`), and the skill
  inventory mapping each skill to its consumer agent. Load when
  editing any `config/skills/*/SKILL.md`.
- **[`references/self-annotation-and-stubs.md`](references/self-annotation-and-stubs.md)**
  — `pycsl_emit` / `rocq2pycsl` / `lean2pycsl` / `pycsl_bridge`
  architecture, the trust chain from formal proof → annotated
  Python, per-package test invocation, and the `src/pycsl_lib/`
  stub convention. Load when working on self-annotation or adding
  library stubs.
- **[`references/test-suite.md`](references/test-suite.md)** —
  Reference test file shape (numbered 0001+ in
  `test-suite/corpus/pycsl-reference/`), the `annotations.md` /
  `traceability-pycsl.md` discipline, and the dual-oracle runner.
  Load when adding a reference test.
- **[`references/why3-quirks.md`](references/why3-quirks.md)** —
  Known Why3 library oddities (`map.Const` export name,
  `list.Nth` option-type, `list.Mem` OOM trap, ghost-array
  syntax, …). Load when debugging an unexpected Module 6
  emission or prover failure.

---

## 9. How to Add a New Feature to PyCSL

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
- **WhyML**: For a new expression shape, add a `_handle_*_expr` handler in `module6_whyml/expressions.py` and register it in `_EXPR_DISPATCH` (still on the `Module6_WhyMLTranspiler` facade). For a new statement shape, add a `_handle_*_stmt` handler in `module6_whyml/statements.py` and wire it into `_stmts_to_whyml`. New `use` / preamble flags go in `module6_whyml/preamble.py`. Per-function emission concerns (signatures, contracts, return-type inference) live in `module6_whyml/functions.py`.
- **bin/ scripts**: If the feature adds or changes a script in `bin/`, update `README.md` (Usage section) — `bin/` scripts are user-facing tools and the README is the primary human documentation
- **glossary terms**: If the feature introduces recurring verification
    vocabulary, add or update the relevant page under `docs/glossary/` and then
    prefer that terminology consistently across docs and skills
- **normative references**: Update all three reference documents in `docs/`
    following conventions in `config/skills/pycsl-docs/SKILL.md`:
    - `docs/pycsl-concrete-syntax-reference.md` — add grammar productions (new atom
        rows in §3.1 Atom Catalogue, new productions in §9 Complete Grammar, update §10.3 gap table)
    - `docs/pycsl-static-semantics-reference.md` — add typing/scope rules (new §3.1.x
        subsection with inference rules, ghost type mapping if applicable)
    - `docs/pycsl-translational-reference.md` — add emission table entries in §T.8 or
        the relevant section; update §T.11 gap codes; update §T.12 method index
    - Bump **Version** in the preamble of each updated document
    - Add `_Corresponds to annotations.md §N._` on each new section
    - Add a gap code (G prefix) if any part of the feature is only partially translated

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

```text
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

### Step 9: Cross-surface documentation coherency

Every new `#@` directive must appear in **all five** normative
surfaces before the PR is review-ready:

1. **`README.md`** — at minimum, a row in the contract-language
   quick-reference table at §"PyCSL Contract Language (Quick
   Reference)" (currently around line 580); a worked example
   section follows when the directive is non-trivial.
2. **`test-suite/annotations.md`** — table row in the appropriate
   subsection (§2.1 function-level, §2.2 loop-level, §2.3
   class-level, §2.4 program-point, §10 concurrent) **plus** a
   detail subsection (`#### §X.Y.Z Directive (...)`) mirroring the
   existing §2.1.13 / §2.2.3 / §2.3.2 format. Never renumber
   existing entries — append at the end of the subsection table.
3. **`docs/pycsl-concrete-syntax-reference.md`** — table row in the
   subsection plus an EBNF production in the grammar block at the
   bottom of the file. Add the directive name to the top-level
   `?contract:` alternative list.
4. **`docs/pycsl-static-semantics-reference.md`** — well-formedness
   inference rule under `#### §X.Y.Z`. State the rule in the form
   used by sibling subsections. If the directive is operationally
   identical to another directive (an alias), state the equivalence
   explicitly with a "Translational alias" or "Informational only"
   paragraph.
5. **`docs/pycsl-translational-reference.md`** — translation rule
   under `### §T.X.Y`. If the directive has no WhyML emission,
   state that explicitly with `T[[#@ ...]] = ()` and the rationale,
   rather than omitting the directive entirely.

Run the audit before opening the PR:

```bash
./bin/doc-coherency.py --check                     # all directives
./bin/doc-coherency.py --check <directive_name>    # one directive
./bin/doc-coherency.py --list-directives           # canonical set
```

The tool walks all five surfaces, extracts directive names from
`test-suite/annotations.md` (the canonical source), and reports
missing entries in each surface. Exits 1 on any gap. Wired into
`bin/run-reference-tests.sh` as a leading gate; skip with
`PYCSL_SKIP_DOC_COHERENCY_CHECK=1`.

Governed by `config/skills/pycsl-doc-coherency/SKILL.md`.

**Worked example.** The `#@ proof <prover> <qualname>` directive
(annotations.md §2.1.12) is the canonical template for cross-prover
proof attribution. It exercises every step of the pipeline: Module2
grammar production, Module5 IR emission, Module6 axiom-block emission
in the WhyML preamble, the `_AXIOM_REGISTRY` extension, and the
audit-script qualname resolution. The provenance-only `#@ proof rocq`
/ `#@ proof lean` directive originally added alongside it was removed
on 2026-05-27 (it carried no semantic weight and had no remaining
users after the delete-heavy triage).

---

## 10. How to Refactor PyCSL Safely (the emission-identical gate)

Refactoring the compiler is different from adding a feature: the goal is **zero behaviour
change**, and "the tests still pass" is too weak a bar. PyCSL is an output-deterministic
transpiler, so a refactor is correct iff the **emitted WhyML is byte-identical** before and
after, across the whole corpus and *every* memory model. Use this as the gate:

1. **Branch + clean baseline from a worktree.** `git worktree add /tmp/pb HEAD`; generate the
   corpus WhyML from `/tmp/pb` (clean) into a baseline dir. The worktree is a separate checkout,
   so you can edit the main tree in parallel while the baseline runs.
2. **Generate WhyML deterministically.** For each `test-suite/corpus/pycsl-reference/*.py`, run
   `PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py <f> --no-proof --keep-mlw <per-file pycsl-flags>`
   and collect the `.mlw`. `PYTHONHASHSEED=0` is mandatory — string-literal ids are `hash()`-based
   and vary per run otherwise (this once produced 11 spurious "diffs" that were pure hash noise).
   Honour each file's `# pycsl-flags:` so model-specific files emit under their model.
3. **Diff.** `diff -rq base after` → **0 diffs, 0 "Only in base"**. Anything else is a regression
   (or a baseline that wasn't clean).
4. **Cover all four memory models.** The differential only validates the branches the corpus
   exercises. Coverage today: `hoare` (default, bulk), `concurrent` (31 files), and `typed`/`store`
   (`0463`–`0470`, added explicitly because the gate honours `# pycsl-flags:`, not the docstring
   `5.2`/`5.3` convention). A refactor that touches the value-semantic-vs-heap split (anything on
   `self._value_semantic`) **must** be diffed with that typed/store coverage present.
5. **Small, individually-diffed commits.** One logical refactor per commit, each gated; if a diff
   ever appears you bisect one change, not a pile.

**CLI / orchestration changes** (`pycsl.py` `main()` / argparse) change control flow, not WhyML,
so the emission differential can't see them. Gate those with `test-suite/cli-behavior-test.sh`
(`PYTHON=.venv/bin/python test-suite/cli-behavior-test.sh`) — exit codes + key output markers
across representative invocations.

For the general (non-PyCSL) refactoring methodology — right-sizing abstractions, treating
recommendations as hypotheses, building coverage before reorganising untested code — see the
`refactor-python` skill (§10–§11). The campaign that hardened both skills lives in
`refactor-recommendations.md`.

---

## 12. Glossary

The `docs/glossary/` directory defines all recurring verification terms:
[ghost code](../../../docs/glossary/ghost-code.md) ·
[ghost state](../../../docs/glossary/ghost-state.md) ·
[ghost lowering](../../../docs/glossary/ghost-lowering.md) ·
[witness](../../../docs/glossary/witness.md) ·
[verification condition](../../../docs/glossary/verification-condition.md) ·
[proof companion](../../../docs/glossary/proof-companion.md) ·
[reference test](../../../docs/glossary/reference-test.md) ·
[trusted stub](../../../docs/glossary/trusted-stub.md) ·
[memory model](../../../docs/glossary/memory-model.md)
