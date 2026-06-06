# plan-formal-05.md — Layer 4: `#@ proof rocq:` / `#@ proof lean:` traceability

**Status:** ⚠️ **Historical document.** The Layer 4 `#@ proof` directives
described here were swept on 2026-05-27 in the delete-heavy triage
documented in `../../proof-to-axiom-from.md`. Only load-bearing
`#@ axiom_from` survives (14 directives in `0342.py`). The
`attic/{rocq,lean}/` historical mirrors referenced below were removed
in the same pass. The text below is preserved as historical context.

**Originally followed:** `plan-formal-04.md` (axiom elevation; partial).

## What's new

The PyCSL proof-attribution directives (`#@ proof rocq: <qualname>` /
`#@ proof lean: <qualname>`) introduced during the `tuesday-01.md`
cross-prover work now link the canonical `src/` annotations to actual
theorems in `src/formal-semantics/{rocq,lean}/`. PyCSL does not
resolve the qualname (per `docs/pycsl-concrete-syntax-reference.md
§2.1.11` v1.3) — the convention is human + future-tooling audit.

The README's Trust Chain gains "Layer 4" describing this layer.

## Pilot: Module5_IREmitter (DONE)

- 16 statement-/expression-emission methods cite the matching
  `wp_gen_<construct>` / `wpGen_<construct>` lemma in
  `Phase6{c,e,f,g}.v` / `Corr{Simple,Loops,Exc}.lean` / `Why3Vcg.lean`.
- 32 `#@ proof` directives total (16 rocq + 16 lean).
- 48 contract clauses (`#@ requires` / `#@ ensures` / `#@ assigns`).
- Lemma↔method mapping table: `module5-mapping.md`.
- Cross-reference audit (`grep`-based) passes: every cited qualname
  resolves to a real `Lemma`/`Theorem` in the formal-semantics tree.
- `pycsl --no-proof src/self-annotate/src/Module5_IREmitter.py` → SUCCESS.
- `make self-annotate-verify` stays green on the `attic/` baseline.

## Recipe (for replicating on Modules 1–4 + 6)

1. **Re-copy clean source.** `cp src/pycsl/Module<N>.py
   src/self-annotate/src/Module<N>.py` to wipe any trivial stub
   annotations. The `attic/{rocq,lean}/` historical references stay
   untouched.
2. **Catalog lemmas → methods.** For each Python method in
   `Module<N>`, find the matching `Theorem`/`Lemma` in
   `src/formal-semantics/rocq/Phase*.v` and `theorem` in
   `src/formal-semantics/lean/PyCSL/*.lean`. Write the mapping to
   `module<N>-mapping.md`. Mark coverage gaps explicitly; do not
   fabricate theorem names.
3. **Annotate each method.** Above every `def`, add a small comment
   citing the source file, then `#@ proof rocq:`, `#@ proof lean:`,
   `#@ requires`, `#@ ensures`, `#@ assigns` lines. Qualname
   convention: `Pycsl.Reference.Module<N>.<lemma>`. Use Rocq's
   snake_case suffix for the rocq directive and Lean's camelCase
   suffix for the lean directive.
4. **Verify.** Three checks:
   - `pycsl --no-proof src/self-annotate/src/Module<N>.py` → SUCCESS.
   - `make self-annotate-verify` → unchanged baseline (CI runs on
     `attic/`, so the new annotations don't regress anything).
   - `grep`-based cross-reference audit (see `module5-mapping.md`
     verification section): every cited qualname must resolve to an
     existing `Lemma`/`Theorem` in `src/formal-semantics/{rocq,lean}/`.

## Module order recommendation (in difficulty / impact order)

| Module | Methods | Status | Lemma source |
|---|---|---|---|
| Module5_IREmitter | ~95 | ✅ DONE (pilot) | `wp_gen_*` in Phase6c/d/e/f/g |
| Module4_SemanticAnalyzer | ~31 | ✅ DONE | `wf_expr`, `wf_expr_safe`, `pycsl_soundness` (Phase1_AST + Phase5b) |
| Module2_Parser | ~150 (mostly leaf handlers) | ✅ DONE | `contract_expr` / `ContractExpr` inductive (Phase1_AST.v / AST.lean) |
| Module3_Weaver | ~10 | ✅ DONE | `func_spec` / `FuncSpec` record (Phase1_AST.v / AST.lean) |
| Module1_Ingestor | ~13 | ✅ DONE (no proof attributions) | no semantic content — pure libCST string extraction |
| Module6_WhyMLTranspiler | ~150+ | ✅ DONE | `wp`, `wp_aug_assign_for_idx`, `ghost_stmt_preserves_reg_state`, `while_inv_preserved`, `pycsl_soundness` |

Module6 is intentionally last — it's the largest and touches every
phase of the formal semantics.

## Module4 outcome (2026-05-26)

- **4 methods cited**: `_validate_contract` → `wf_expr` / `WfExpr`;
  `_build_function_scope` → `wf_expr` (Γ construction);
  `_validate_function_contracts` → `wf_expr_safe` / `wfExprSafe`;
  `process` → `pycsl_soundness` (both languages).
- **Coverage gaps**: 27 helper methods (concurrency analysis, AST
  walkers, sub-validators) keep structural-only contracts; documented
  in `module4-mapping.md`.
- **Verification**: `pycsl --no-proof` SUCCESS;
  `make self-annotate-verify` baseline unchanged; all 4 Rocq + 4 Lean
  qualname cross-references resolve.

## Module2 outcome (2026-05-26)

- **2 entry-point methods cited**: `parse_contract` and
  `parse_node_contracts`, both attributed to the `contract_expr`
  (Rocq) / `ContractExpr` (Lean) inductive. The ~120 Lark-Transformer
  leaf methods are deliberately *not* individually cited — each one
  is a single-constructor wrapper, and the umbrella attribution at
  the parse-entry sits one level higher (per `module2-mapping.md`).
- **Coverage gaps**: ~70 CSLNode dataclass declarations + ~120
  PyCSLTransformer leaf methods + a handful of helpers. All carry no
  `#@ proof` line. The dataclass-as-inductive-constructor pattern is
  documented in the mapping table.
- **Verification**: `pycsl --no-proof` SUCCESS;
  `make self-annotate-verify` baseline unchanged; the 1 Rocq + 1 Lean
  cited inductive resolves.

## Module3 outcome (2026-05-26)

- **2 entry-point methods cited**: `visit_FunctionDef` (per-function
  attachment) and `process` (top-level whole-AST traversal), both
  attributed to `func_spec` (Rocq) / `FuncSpec` (Lean). The other
  visitor methods (`visit_Module`, `visit_ClassDef`, `visit_With`,
  `visit_While`, `visit_For`) are sub-cases of the function-spec
  construction and inherit the umbrella attribution.
- **Coverage gaps**: 5 visitor sub-helpers + 2 `__init__` methods.
  No `#@ proof` lines on these.
- **Verification**: `pycsl --no-proof` SUCCESS;
  `make self-annotate-verify` baseline unchanged; the 1 Rocq + 1 Lean
  cited record/structure resolves.

## Module1 outcome (2026-05-26)

- **Zero proof attributions** — Module1 is pure libCST string
  extraction; the formal semantics begins one step downstream at
  `contract_expr`. Per the coverage-gap policy ("do not fabricate
  theorem names"), no `#@ proof` line was added to any method.
  Documented in `module1-mapping.md`.
- **Verification**: `pycsl --no-proof` SUCCESS;
  `make self-annotate-verify` baseline unchanged; 0/0 cross-refs (no
  audit failures since there's nothing to audit).

## Module6 outcome (2026-05-26)

- **11 methods cited**: statement handlers (`_handle_assign_stmt`,
  `_handle_while_stmt`, `_handle_for_stmt`, `_handle_try_stmt`,
  `_handle_if_stmt`, `_handle_array_set_stmt`, `_handle_return_stmt`,
  `_handle_critical_section_stmt`, `_handle_augassign_stmt`,
  `_handle_ghost_assign_stmt`) each cite the matching `wp` arm or a
  specific soundness lemma (`while_inv_preserved`,
  `wp_aug_assign_for_idx`, `ghost_stmt_preserves_reg_state`);
  `transpile` (top-level) cites `pycsl_soundness`.
- **Coverage gaps**: ~40 expression handlers, all `_emit_preamble_*`
  scaffolding, and ~80 sub-helpers. The umbrella attribution at
  `transpile` covers the whole-program soundness claim.
- **Verification**: `pycsl --no-proof` SUCCESS;
  `make self-annotate-verify` baseline unchanged; all 4 distinct
  Rocq lemmas + 3 distinct Lean theorems cited (across 11 directives
  each side) resolve.

## Layer 4 rollout summary

| Module | Proof rocq lines | Proof lean lines |
|---|---|---|
| Module1 | 0 | 0 |
| Module2 | 2 | 2 |
| Module3 | 2 | 2 |
| Module4 | 4 | 4 |
| Module5 | 16 | 16 |
| Module6 | 11 | 11 |
| **Total** | **35** | **35** |

The trust chain's Layer 4 (proof-attribution traceability) is now
complete across the canonical `src/self-annotate/src/` corpus.

**CI integration (2026-05-26)**: ✅ `make self-annotate-verify` now
runs `pycsl --no-proof` over all 11 files in `src/self-annotate/src/`
in addition to the existing `attic/rocq/` and `attic/lean/` passes.
Any regression in the Layer-4-annotated canonical files breaks CI
immediately.

**Remaining follow-up (still out of scope)**: a grep-based
qualname-resolution audit (the `bin/check-proof-attributions.sh`
script mentioned earlier) that confirms every `#@ proof rocq:` /
`#@ proof lean:` qualname maps to an actual
`Lemma`/`Theorem`/`Inductive`/`Record`/`Fixpoint`/`def`/`structure`
in `src/formal-semantics/{rocq,lean}/`. Currently this audit is run
manually (the snippet at the end of each `module<N>-mapping.md`).

## Gating CI on the new annotations (future work)

`make self-annotate-verify` currently runs only over `attic/`. A
follow-up plan should extend it to `src/` so the pilot's verification
runs every commit. The patch is small (loop over `src/self-annotate/src/*.py` too) but should be its own change so any breakage is
debuggable.

## Effort estimate

Per module (after the Module5 pilot's recipe is in hand): ~2 h for
small modules (1–4), ~6–8 h for Module6. Total: ~16–22 h spread over
6 sessions.
