# 28-self-annotate.md — Self-annotation status & re-sync plan

**Date:** 2026-06-28
**Status:** Plan (arising from a staleness audit of `src/self-annotate/` and `src/formal-semantics/`)
**Context:** PyCSL has implemented `os` (stdlib) and `typing` (12 constructs, TY0–TY3), migrated Module2 off Lark, and bumped IR_VERSION 1.2 → 1.4. The self-annotation artifacts predate most of this work and have drifted.

---

## 1. What self-annotation claims to be

`src/self-annotate/src/` holds annotated COPIES of `src/pycsl/` files, intended to prove the compiler with itself. The copies carry heavy `#@` contracts; the goal is that each compiler file verifies under `pycsl`.

## 2. Finding: the copies have drifted from the originals

The self-annotate copies were last touched 2026-06-26 (the TY1 Final commit). The `src/pycsl/` originals moved on through the rest of TY1, all of TY2/TY3, the formal-tests commit, the `.claude` symlink, and the **Lark-free Module2 migration** (2026-06-27). The line counts and contract counts diverge sharply:

| File | self-annotate (lines / `#@`) | src/pycsl (lines / `#@`) | Drift |
|---|---|---|---|
| `pycsl.py` | 908 / 92 | 1345 / 7 | massive |
| `Module6_WhyMLTranspiler.py` | 325 / 42 | 937 / 19 | massive |
| `exception_model.py` | 137 / 12 | 203 / 1 | large |
| `audit_proof.py` | 504 / 72 | 509 / 9 | large |
| `ir_schema.py` | 147 / 5 | 234 / 2 | medium |
| `errors.py` | 46 / 1 | 71 / 1 | medium |
| `import_classifier.py` | (in sa) | changed | medium |

**The 6 files that currently prove** (`errors`, `ir_schema`, `Module6_WhyMLTranspiler`, `audit_proof`, `exception_model`, `pycsl`) are proving **stale snapshots** — not the code that runs. The proofs are valid for an older compiler, not for the current one.

## 3. Finding: the bulk of the compiler is not annotated at all

### 3.1 Missing top-level files (in `src/pycsl/`, absent from `self-annotate/src/`)
- `core_ir_semantic.py` (1685 lines) — the static-semantics checker, central to the typing work
- `audit_proof_reverify.py` (420 lines)
- `proof_axiom_allowlist.py` (101 lines)

### 3.2 Missing subdirectories (0 files annotated)
- **`frontend/` (13 files)** — the parser front-end. Includes `pure_ast.py` (3827 lines, the Lark-free parser we just landed), `Module2_Parser.py` (2168 lines, the contract grammar — now Lark-free), `Module5_IREmitter.py` (the IR emitter, heavily touched by typing), `Module3_Weaver.py`, `import_classifier.py`, `module_collect.py`, `monomorphize.py`, `ir_resolve.py`.
- **`proof2why3/` (13 files)** — the Rocq/Lean proof extraction. 0 files annotated.
- **`agents/` (the LLM-orchestration layer)** — out of scope for self-annotation (not part of the verifier core; they *run* PyCSL).

### 3.3 `module6_whyml/` — present but all drifted + 4 files missing
11 of 15 files are in self-annotate but ALL have drifted. The 4 **missing** files are exactly the ones the typing engagement touched:
- `stmt_control_flow.py` (the Union/Optional narrowing + match exhaustiveness lowering)
- `expr_ghost_collections.py`
- `expr_ghost_spec_ops.py`
- `struct_format.py`

## 4. Finding: `src/formal-semantics/` is also stale

The Rocq + Lean mechanization of PyCSL's WP calculus (`pycsl_soundness` theorem) was last touched 2026-06-06 — **3 weeks before** the current `src/pycsl/`. The soundness theorem itself (0 Admitted / 0 sorry) is a **model-level** proof, less brittle than line-by-line self-annotation, but:
- It models a subset of the IR. Since 2026-06-06, IR_VERSION went 1.2 → 1.4 (the `is_noreturn` flag, `type_params`, `final_registry`, typing-variant synthesis, monomorphization fields). None of these are in the model.
- `src/formal-semantics/audit-plan.md` (the feature→proof traceability map) catalogs features as of early June — before the 12 typing constructs landed. It is stale.

## 5. The re-sync plan

### Phase A — Re-sync the drifted copies (stop the bleeding)
For each of the 6 drifted files in `self-annotate/src/`, re-sync the source from `src/pycsl/` and re-validate the contracts. Several will break (the Lark migration changed `Module2`'s internals; the typing work changed `Module5`/`Module6`; `pycsl.py` grew 437 lines).

1. Copy the current `src/pycsl/<file>.py` over `self-annotate/src/<file>.py`.
2. Re-apply the existing `#@` contracts (they were written for an older version; adjust for the new code shape).
3. Run `pycsl self-annotate/src/<file>.py` — iterate until SUCCESS.
4. Files in scope (ordered by blast radius): `pycsl.py`, `Module6_WhyMLTranspiler.py`, `audit_proof.py`, `exception_model.py`, `ir_schema.py`, `errors.py`, `import_classifier.py`.

**Gate:** the 6 currently-passing files still pass, against the CURRENT `src/pycsl/` source.

### Phase B — Re-sync `module6_whyml/` + add the 4 missing files
1. Re-sync the 11 drifted `module6_whyml/*.py` copies from `src/pycsl/module6_whyml/`.
2. Add the 4 missing files (`stmt_control_flow.py`, `expr_ghost_collections.py`, `expr_ghost_spec_ops.py`, `struct_format.py`) — annotate from scratch.
3. Re-validate all 15.

**Gate:** `module6_whyml/` fully annotated and proving, 15/15.

### Phase C — Annotate the missing top-level files
- `core_ir_semantic.py` (1685 lines) — the static-semantics checker; large, likely needs splitting or careful `no_inline`.
- `audit_proof_reverify.py` (420 lines).
- `proof_axiom_allowlist.py` (101 lines).

**Gate:** all top-level `src/pycsl/*.py` annotated and proving.

### Phase D — Annotate `frontend/` (13 files, the heaviest tier)
This is the largest un-annotated block and the most valuable (the parser is what makes PyCSL a verifier):
- `pure_ast.py` (3827 lines) — the Lark-free Python parser. Large; may need decomposition.
- `Module2_Parser.py` (2168 lines) — the Lark-free contract parser (just migrated).
- `Module5_IREmitter.py` — the IR emitter (heavily touched by typing).
- `Module3_Weaver.py`, `import_classifier.py`, `module_collect.py`, `monomorphize.py`, `ir_resolve.py`, and the remaining frontend files.

**Gate:** `frontend/` fully annotated and proving.

### Phase E — Annotate `proof2why3/` (13 files)
The Rocq/Lean proof extraction layer. Lower priority (it's a post-hoc tool, not the verification core), but needed for full self-coverage.

### Phase F — Refresh `src/formal-semantics/audit-plan.md`
Update the feature→proof traceability map to reflect:
- The 12 typing constructs (Union, Optional, Literal, cast, Final, NoReturn, TypedDict, NamedTuple, overload, Protocol, TypeVar/Generic, Callable).
- The IR 1.4 fields (`is_noreturn`, `type_params`, `final_registry`).
- Note which are modeled in the Rocq/Lean soundness proof and which are out-of-model (the typing constructs are likely out-of-model — they're IR-emitter features, not WP-calculus features).

**Gate:** `audit-plan.md` accurately reflects the current feature set.

## 6. Scope boundaries

### In scope
- Re-syncing drifted copies (Phase A/B).
- Annotating the missing compiler-core files (Phases C/D/E).
- Refreshing the formal-semantics traceability map (Phase F).

### Out of scope
- `agents/` (the LLM-orchestration layer) — not the verifier core.
- Re-proving the Rocq/Lean `pycsl_soundness` theorem for the new IR fields — that's a separate formal-semantics effort (the model is soundness-level, not line-by-line). Phase F only refreshes the *map*, not the proof.

## 7. Sequencing & dependencies

- **Phase A first** — it's the cheapest and stops the "proving stale code" problem immediately. The 6 files already prove; re-syncing is mechanical.
- **Phase B before C/D** — `module6_whyml/` is smaller than `frontend/` and the 4 missing files are the typing-affected ones (high value).
- **Phase D (frontend) is the long pole** — `pure_ast.py` (3827L) and `Module2_Parser.py` (2168L) are large; may need decomposition before they'll annotate. This is where refactoring MIGHT become necessary — but only if a specific file blocks, not speculatively.
- **Phase F can run in parallel** with any phase (it's documentation, not code).

## 8. Effort estimate

| Phase | Effort | Risk |
|---|---|---|
| A — re-sync 6 drifted files | Medium — mechanical copy + contract adjustment | Low (they already proved; re-sync is mostly re-validation) |
| B — re-sync module6_whyml + 4 new | Medium-High — 4 files from scratch | Medium (stmt_control_flow is complex) |
| C — 3 missing top-level files | Medium — core_ir_semantic is large | Medium (may need no_inline) |
| D — frontend (13 files) | High — pure_ast 3827L, Module2 2168L | High (decomposition likely needed) |
| E — proof2why3 (13 files) | Medium | Low (post-hoc tool) |
| F — audit-plan refresh | Low — documentation | None |

**Critical path:** A → B → C → D. Phases E and F can overlap. Phase D is the long pole and the only place a refactor may be warranted (driven by proof failures, not speculation).
