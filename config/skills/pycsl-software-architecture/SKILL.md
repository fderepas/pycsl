---
name: pycsl-software-architecture
description: Describe the reference architecture for the PyCSL codebase. Covers the 6-module compiler pipeline (Ingestor → Parser → Weaver → SemanticAnalyzer → IREmitter → WhyMLTranspiler), the data formats between modules, the agent orchestration layer, the error hierarchy, the three memory models (hoare/typed/store), and the infrastructure scripts. Use when maintaining, extending, or debugging the compiler pipeline, agents, memory models, error handling, or infrastructure in the PyCSL repository.
---

# PyCSL Software Architecture

PyCSL is a Python-to-WhyML compiler. It reads a Python source file annotated with `#@` contract comments and produces a WhyML (`.mlw`) file that Why3 can verify formally. This skill describes the full architecture for agents maintaining or extending the codebase.

---

## Section 1 — Repository layout

```text
src/pycsl/
  Module1_Ingestor.py         ← LibCST CST walk → List[PyCSLContract]
  Module2_Parser.py           ← Lark LALR → CSLNode AST
  Module3_Weaver.py           ← weaves CSLNode into ast.AST (in-place csl_* fields)
  Module4_SemanticAnalyzer.py ← validates annotated ast.AST
  Module5_IREmitter.py        ← annotated ast.AST → JSON IR string
  Module6_WhyMLTranspiler.py  ← facade; JSON IR string → WhyML text
  module6_whyml/
    ir_scanner.py             ← stateless IR-tree analysis
    identifiers.py            ← whyml_ident / safe_mutex_name / op_translate + OP_MAP, WHYML_RESERVED
    scc.py                    ← Tarjan SCC + call-graph helpers for function emission order
    auto_trust.py             ← AutoTrustMixin: auto-trust decisions + linear-VC classification
    abstract_ops.py           ← AbstractOpsMixin: abstract-val registry + late insertion
    types.py                  ← TypeInferenceMixin: RHS classification + field-type + collection metadata
    expressions.py            ← ExpressionEmissionMixin: _EXPR_DISPATCH targets + expr-emission helpers
    statements.py             ← StatementEmissionMixin: _handle_*_stmt + body wrapping + frame condition
    preamble.py               ← PreambleEmissionMixin: use/exceptions/helpers/axioms + shared state + type decls
    functions.py              ← FunctionEmissionMixin: per-function emission + param typing + contracts + cross-method maps
  pycsl.py                    ← CLI entry point
  errors.py                   ← PyCSLError hierarchy
  ir_schema.py                ← validate_ir() — JSON IR structural contract
  agents/                     ← LLM-based annotation and proof orchestration

config/skills/                ← skill markdown files consumed by agents via RAG
test-suite/corpus/            ← reference tests (pycsl-reference/), negative tests
bin/                          ← shell scripts (run-reference-tests.sh, annotate.sh, …)
src/skill2rag/                ← indexes config/skills/ into a Chroma vector store
data/                         ← Why3 stdlib stubs, lib_stubs/ Python stubs
```

---

## Section 2 — The 6-module compiler pipeline

Each module is a class instantiated with its input; callers chain them in order inside `_run_pipeline()` in `src/pycsl/pycsl.py`.

| # | Class | Constructor input | Output | Key library |
|---|-------|-------------------|--------|-------------|
| 1 | `Module1_Ingestor(source_code)` | Python source text (`str`) | `List[PyCSLContract]` | LibCST + PositionProvider |
| 2 | `Module2_Parser` (static `parse()`) | `List[PyCSLContract]` | `List[PyCSLContract]` with `.contracts` as `List[CSLNode]` | Lark LALR (`csl.lark`) |
| 3 | `Module3_Weaver(contracts_map, source_code, extracted_data, parser_module)` | `List[PyCSLContract]` | annotated `ast.AST` (in-place `csl_*` fields) | stdlib `ast` |
| 4 | `Module4_SemanticAnalyzer` (static `analyze()`) | annotated `ast.AST` | validated AST or raises `PyCSLSemanticError` | — |
| 5 | `Module5_IREmitter(tree)` | annotated `ast.AST` | JSON string (`json.dumps`) | — |
| 6 | `Module6_WhyMLTranspiler(json_ir, memory_model)` | JSON string + model name | WhyML text (`str`) | — |

For the data formats produced at each stage, see `references/data-formats.md`.

---

## Section 3 — Error hierarchy (`src/pycsl/errors.py`)

```text
PyCSLError(Exception)       base — fields: message, filename, line, stage
  ├── PyCSLParseError        Module2: CSL grammar parse failure
  ├── PyCSLSemanticError     Module4: semantic validation failure
  └── PyCSLIRError           Module5: unsupported CSL node during IR emission
```

**Rules:**
- All library code (Modules 1–6, IR schema) raises `PyCSLError` subclasses — never `sys.exit`.
- `sys.exit(1)` is used only in `pycsl.py main()` after catching `PyCSLError`.
- `str(error)` includes the stage, filename, and line number when set.

---

## Section 4 — Memory models (Module6)

The `memory_model` constructor parameter controls how Python arrays are represented in WhyML:

| Model | Value | Array semantics | Heap variable |
|-------|-------|-----------------|---------------|
| Hoare | `"hoare"` | Value-semantic `array int` — no heap aliasing | None |
| Typed | `"typed"` | Heap-based `loc` reference type | `int_mem` |
| Store | `"store"` | Heap-based `store` record | `store` |

Default is `"hoare"`. Controlled by `--memory-model` on the `pycsl` CLI, or by a `--memory-model` line in a test's `header` file.

---

## Section 5 — Shared agent utilities (`src/pycsl/agents/`)

Two always-importable shared modules:

**`common.py`** — import from here in any agent:
- `log(path, name, message)` — appends timestamped line to `<path>/log/<name>.log`
- `retrieve_skill_chunks(queries, config_path)` — RAG retrieval from the Chroma skill index
- `extract_code_block(text, language)` — extracts a fenced code block from LLM output
- `load_config(config_path)` — reads and returns `agents-config.json` as a dict

**`llm_client.py`** — LLM calls:
- `llm_generate(prompt, system, agent_id, model)` — dispatches to Ollama or GitHub Copilot
- `ollama_generate(prompt, system, temperature, agent_id)` — direct Ollama call
- `githubcopilot_generate(prompt, system, agent_id, model)` — GitHub Copilot REST call
- `write_next_sequential_file(dirname, prefix, data)` — writes numbered output files
- re-exports `log` from `common` for backward compatibility

**Critical constraint:** `common.py` must not import from agent modules — it is the shared leaf, not a hub.

For the full agent orchestration description, see `references/agent-pipeline.md`.

---

## Section 6 — How to extend the compiler and agents

**Adding a new CSL keyword (e.g., a new contract type):**
1. `Module2_Parser.py` — add grammar rule to `csl.lark` and a new `CSLNode` dataclass.
2. `Module3_Weaver.py` — attach it to the appropriate `ast` node as a new `csl_*` field.
3. `Module4_SemanticAnalyzer.py` — add validation logic.
4. `Module5_IREmitter.py` — emit the new field into the JSON IR dict.
5. `ir_schema.py` — extend `validate_ir()` if the field is required.
6. `module6_whyml/expressions.py` or `module6_whyml/statements.py` — add the handler function and register it in `_EXPR_DISPATCH` (on the facade) for new expression shapes, or wire it into `_stmts_to_whyml`'s dispatch for new statement shapes.
7. Add a reference test in `test-suite/corpus/pycsl-reference/`.

**Adding a new guard to agent-annotate:**
Guards are `str → str` transforms applied by `GuardPipeline`. Add a `_guard_*` or `_fix_*` function and register it with `pipeline.apply("guard-name", _your_function)`. Each guard must be idempotent and independently testable by calling it directly on a string.

**Adding a new agent:**
1. Create `src/pycsl/agents/agent-<name>.py` with `AGENT_NAME = "agent-<name>"`.
2. Import `log` from `common`, `llm_generate` from `llm_client`.
3. Register skill queries in `agents-config.json` under the agent name.
4. Wire it into `coordinator.py` at the appropriate step.
