# self-tcb-reduction.md — shrink the self-annotation trusted core toward its irreducible floor

**Purpose.** The self-annotation mirror (`src/self-annotate/src/`) carries **≈1290 `\trusted`
stubs** (one `#@ \trusted reviewer: pycsl-self-annotate` marker each) against only **24 verified
body-faithful methods** (the completed 18-handler statement-emitter campaign + ~6 supporting
methods). This plan is the long-horizon campaign to convert those stubs — tier by tier, highest
soundness-value first — into verified bodies, driving the trusted core down to its **irreducible
floor**.

**Honest target (read this first).** "Remove all 1296" is **not achievable and not the goal.** A
hard floor is irreducible by design (Ceiling B, Gödel-2/Löb — see `remaining-trust.md`,
`item34.md §1`): the recursion leaves `_expr_to_whyml` / `_stmts_to_whyml` and the 37 D2 evaluator
axioms in `pycsl-wp-spec.mlw` **must stay trusted** — a system cannot prove its own evaluator
sound. The target is therefore **"reduce ≈1290 → the floor"**, where the floor is a *small,
enumerated, audited* set (the leaves + the genuinely-opaque boundaries), NOT zero. Every stub this
plan cannot convert must be *reclassified* into that audited floor with a reason, not left as
undifferentiated trust.

**Doctrine.** Same as the 18-handler campaign: each conversion is **port-verbatim → verify
(type-safety + `assigns` frame) → byte-diff 0 across the 627-corpus → un-`\trust` → both
mirror-sync gates green**. `@mutable_state`/emit_ir-gated recognizers only; the corpus never
changes. **Demand-gated** (`pycsl-how-to-develop §8.2`): convert stubs that carry soundness weight
or that a verified caller needs — do not gold-plate the low-value tail.

---

## 0. Where we start — the ≈1290 stubs by tier (measured 2026-07-03)

| Tier | Scope | ≈ stubs | Soundness weight | Tractability |
|---|---|---:|---|---|
| **T1** | **Module 6 emitter** (`module6_whyml/` + `Module6_WhyMLTranspiler.py`) | **~326** | **HIGH** — the Layer-3 (coherence) load-bearing path | **PROVEN** (18 handlers already done) |
| **T2** | **Semantic analyzer** (`core_ir_semantic.py`) | ~66 | HIGH — Layer-1 structural faithfulness | new contract class (analyzer invariants) |
| **T3** | **Front-end pipeline** (`frontend/`: pure_ast 262, Module5 180, Module2 91, Module3 39, monomorphize 25, ir_resolve 21, Module1 18, ir_inline 17, …) | ~671 | MEDIUM — structural; Layer-2 re-checks output anyway | harder (preservation contracts, not WhyML type-safety) |
| **T4** | **Tooling / orchestration** (`proof2why3/` 118, `pycsl.py` 39, `audit_proof*` 29, `exception_model` 6) | ~192 | LOW — provenance tooling + CLI glue | mixed; mostly YAGNI |

T1 sub-breakdown (the immediate work): `expressions.py` 79 (incl. **24 `_handle_*_expr`
expression handlers** — the direct analog of the done statement handlers), `statements.py` 43
(remaining helpers), `functions.py` 37, `ir_scanner.py` 34, `preamble.py` 25,
`expr_ghost_collections.py` 24, `types.py` 18, `expr_ghost_spec_ops.py` 12, `auto_trust.py` 12,
`struct_format.py` 6, `identifiers.py`/`scc.py` 5, `abstract_ops.py` 4, `Module6_WhyMLTranspiler.py`
22.

---

## 1. The irreducible floor (what STAYS trusted — enumerate, don't shrink)

Before converting anything, fix the floor so "done" is well-defined:

- **F1 — the recursion leaves.** `_expr_to_whyml`, `_stmts_to_whyml` (and any mutually-recursive
  emitter sibling that bottoms out in them). Ceiling B. Stay `\trusted / ensures True`.
- **F2 — the D2 evaluator axioms.** The 37 axioms in `pycsl-wp-spec.mlw` (audited by I3.1). Not
  `.py` stubs, but part of the floor.
- **F3 — genuinely-opaque boundaries.** Any method whose faithful contract would require modelling
  an external/undecidable surface (SMT solver invocation, file I/O in the CLI, subprocess to
  `why3`, the `agents/` LLM calls). These are `\abstract`/`\trusted` with a *documented* boundary
  (`pycsl-how-to-develop §8.4` — sound under-approximation, never a fake axiom).

**Deliverable of every tier:** each stub is either (a) converted to a verified body, or (b)
*re-sited* into F1/F2/F3 with a one-line reason in `arm-coverage.md`. No stub may remain
un-classified.

---

## 2. Stages (each stage = a batch of stubs; the per-stub loop is fixed)

### T1 — Module 6 emitter (do first: highest value × proven tractability)

- **T1.a — the 24 expression handlers** (`_handle_*_expr` in `expressions.py`). The exact analog
  of the 18 statement handlers: port verbatim, `#@ requires True / ensures True / assigns
  <frame>`, extend the recognizers where a reflective construct leaks, byte-diff 0, un-`\trust`.
  Start with the read-only ones (`_handle_var_expr`, `_handle_attribute_expr`,
  `_handle_field_get_expr`) — cheapest end-to-end; end with the broadest (`_handle_call_expr`,
  `_handle_fstring_expr`).
- **T1.b — the emitter helpers** (`types.py`, `functions.py`, `preamble.py`, `ir_scanner.py`,
  `abstract_ops.py`, `auto_trust.py`, `identifiers.py`, `scc.py`, `struct_format.py`,
  `expr_ghost_*`). Mostly pure/structural — many are `assigns \nothing` leaves that verify
  quickly. Convert in dependency order (a verified handler's callees first).
- **Gate (T1):** every `module6_whyml` method is verified OR in F1/F3; `check-self-annotate-sync.sh`
  green; byte-diff 0; the whole coherence path (Layer 3) now rests only on F1+F2.

### T2 — the semantic analyzer (`core_ir_semantic.py`, ~66)

Layer-1 structural faithfulness: contracts here are **analyzer invariants** (type-environment
well-formedness, scope preservation, exhaustive case handling), NOT WhyML type-safety. New
contract class — spike one method first to fix the pattern, then batch.

### T3 — the front-end pipeline (`frontend/`, ~671)

The bulk of the count, the least soundness weight (Layer 2 re-checks the emitted WhyML on every
run, so a front-end defect cannot pass silently). Verify **structural-preservation** contracts
(Layer-A style: `#@ ensures \forall i … \result[i] is not None`, `assigns \nothing`, no dropped
nodes). Order by leaf-first: `Module1_Ingestor` (small), then `ir_resolve`/`ir_inline`/
`monomorphize`, then the big three (`pure_ast`, `Module5_IREmitter`, `Module2_Parser`) as their own
sub-campaigns. **Explicitly demand-gated** — this tier only earns its cost if a driver (or an
external audit requirement) demands front-end faithfulness; otherwise it stays a documented,
lower-priority surface.

### T4 — tooling / orchestration (`proof2why3/`, `pycsl.py`, `audit_proof*`, ~192)

**Lowest value; default to F3 (documented boundary), not conversion.** `pycsl.py` is CLI glue over
`why3`/file-I/O (F3). `proof2why3/` is proof-provenance tooling, off the soundness path. Convert
only the handful with real logic if a demand appears; otherwise re-site into F3 with a reason.
**This tier is expected to end mostly re-classified, not verified.**

---

## 3. Ordering rationale & realistic scope

- **Value gradient:** T1 (emitter) directly reduces what Layer 3 trusts → do first. T2 (analyzer)
  strengthens Layer 1. T3/T4 add structural coverage but Layer 2 already backstops them → later /
  demand-gated.
- **This is a multi-month campaign, not a sprint.** The 18-handler statement campaign — one tier's
  worth — spanned many sessions. Budget T1 as *the* next arc (≈326 stubs, but many are trivial
  `assigns \nothing` leaves), T2 as a focused follow-on, T3 as a standing background reduction, T4
  as reclassification.
- **The honest end state** is NOT 0 trusted. A realistic floor is **F1 (≈2–10 leaf methods) + F2
  (37 axioms) + F3 (the documented opaque boundaries)** — plausibly reducing the ≈1290 `.py` stubs
  to a low-tens *audited* core, with T4 re-sited rather than removed.

---

## 4. Critical files

- `src/self-annotate/src/module6_whyml/*.py` — the T1 mirror (port + un-`\trust`).
- `src/pycsl/module6_whyml/*.py` — incremental `@mutable_state`-gated recognizer additions (a stub
  may surface a new leak the way the statement handlers did).
- `src/self-annotate/src/core_ir_semantic.py`, `frontend/*.py` — T2/T3 mirrors.
- `src/self-annotate/arm-coverage.md` — the floor register (F1/F3 re-siting reasons).
- `bin/check-self-annotate-mirror-sync.py` / `bin/self-annotate-mirror-check.sh` — the gates;
  extend the 0-trusted lint to *report the shrinking count* per tier.

---

## 5. Out-of-scope / soundness boundary

- **The floor (F1/F2/F3) stays trusted** — no attempt to un-`\trust` the recursion leaves
  (Gödel/Löb); no fake axiom.
- **Corpus untouched** — every recognizer `@mutable_state`/reflection-gated; byte-diff 0 is the
  gate on every stub.
- **Type-safety + frame** (and, for T2/T3, structural-preservation) — NOT value-faithful
  `ensures \result == <string>` (that bottoms out at F1/Ceiling B).
- **Demand-gating is a real off-ramp** — T3/T4 stubs with no soundness weight and no verified
  caller may be *documented-and-deferred* indefinitely; that is a legitimate closed state.

---

## 6. Verification (per stub + per tier)

```bash
# per stub: type-check + byte-diff 0
python3 src/pycsl/pycsl.py <mirror-file> --import-path src/pycsl --no-proof
PYTHONHASHSEED=0 bash bin/byte-diff-sweep.sh /tmp/after && diff -rq <clean-baseline> /tmp/after
# per tier: full proof + gates + shrinking trusted count
python3 src/pycsl/pycsl.py <mirror-file> --import-path src/pycsl          # full proof
bash bin/check-self-annotate-sync.sh && bash bin/self-annotate-mirror-check.sh
find src/self-annotate/src -name '*.py' -exec grep -h '\trusted' {} \; | wc -l   # must shrink
bash bin/run-self-annotation-suite.sh                                     # no new failures
```

## 7. Reference corpus

Like the emitter campaign, the surface is **self-annotation-internal** (reflection over the tool's
own IR requires `--import-path`), so a standalone corpus witness is not viable (see `cf6.md §3`) —
**the mirror is the driver**, exercised by `bin/run-self-annotation-suite.sh`; the 627-corpus
byte-diff-0 gate proves additivity. Where a T1 conversion adds a genuinely new emit_ir projection,
add a `@mutable_state` witness per `pycsl-how-to-develop §8.2` if it can verify standalone.

---

## 8. Progress ledger (live)

| Tier | Scope | Start | Verified | `\trusted` remaining | Status |
|---|---|---:|---:|---:|---|
| (done) | Module 6 statement handlers | — | 18 + 6 | — | ✅ COMPLETE |
| F1/F2/F3 | irreducible floor (enumerate) | — | — | — | ◻ TODO (fix the floor first) |
| T1.a | expression handlers (`_handle_*_expr`) | 24 | 0 | 24 | ◻ TODO |
| T1.b | Module 6 emitter helpers | ~302 | 0 | ~302 | ◻ TODO |
| T2 | semantic analyzer | ~66 | 0 | ~66 | ◻ TODO |
| T3 | front-end pipeline | ~671 | 0 | ~671 | ◻ demand-gated |
| T4 | tooling / orchestration | ~192 | 0 | ~192 | ◻ re-site to F3 (mostly) |

**Definition of done.** Every `.py` stub in the mirror is either (a) a verified body or (b)
enumerated in the F1/F3 audited floor with a reason; the `wc -l` trusted count is reduced to that
floor; `check-self-annotate-sync.sh`, `self-annotate-mirror-check.sh`, and
`run-self-annotation-suite.sh` all green; byte-diff 0 throughout.

---

## 9. Execution vehicle — the `self-tcb-reduction` Squeeze Loop (SL)

This campaign is executed as a **Squeeze Loop** (see `config/skills/sl-internal`): every stub
conversion is held between a soft **upper bound `U`** and a hard **lower bound `L`**, and the
actors are **disjoint** so the dominant *coherent-and-wrong* failure is always caught by an actor
that cannot share the blind spot. The loop is packaged as the skill
`config/skills/self-tcb-reduction/` (`SKILL.md` + `self-tcb-reduction.json`).

- **Terrain: A (transcription) + C (split planes).** The live emitter exists on disk — the
  converter *transcribes* it verbatim; and "correct" splits across **three disjoint oracle
  planes** that must never blend: **fidelity** (mirror-sync: the mirror body == the live body),
  **type-safety** (Why3 discharges the `assigns`-framed contract), **corpus-inertness** (byte-diff
  0 across the 627-corpus).
- **`U`** = the live emitter method + the fixed contract shape (`requires True / ensures True /
  assigns <frame>` — *not* value-faithful, *not* vacuous) + the item-3 ceiling doctrine.
- **`L`** = `check-self-annotate-sync.sh` ∧ Why3 proof discharge ∧ `diff -rq` byte-diff 0 ∧
  `run-self-annotation-suite.sh` ∧ a strictly-shrinking `\trusted` `wc -l`.
- **Dominant coherent-and-wrong (guard these):** (1) silent **mirror drift** — a stub that
  "verifies" a stale copy → caught by the fidelity gate; (2) **corpus perturbation** — a recognizer
  that quietly changes real-program output → caught by byte-diff 0; (3) **reclassification dodge**
  — mislabelling a convertible stub as "irreducible floor" to skip the work → caught by an
  independent **floor-auditor** demanding a Gödel/Löb-class reason; (4) **fake-axiom / weakened
  frame** → caught by the `proof_axiom_allowlist` + assigns-tightness check.
- **Actors (disjoint `(U,L)`):** **coordinator** (sequences tiers, delegates one stub, renders
  gate verdicts, owns the shrinking-count ledger; never edits code, never rubber-stamps);
  **converter** (transcribes the live body + contract + `@mutable_state`-gated recognizers; never
  sees the corpus baseline or the floor-audit; may not weaken a contract or add an axiom);
  **verifier** (runs the three oracle planes *fresh from the surface only*; never reads the
  converter's recognizer rationale); **floor-auditor** (judges every *re-siting* to the floor
  against the ceiling doctrine — PASS / REJECT; the coherent-and-wrong catcher for the dodge);
  optional **triage probe** (one-shot parallel classification of all stubs into
  trivial-leaf / needs-recognizer / hard-architectural / floor).
- **Escalate, don't thrash:** a per-stub attempt budget; on exceed, revert and flag for a focused
  pass (the hard-architectural ones like `match` were whole sessions) — the loop harvests the easy
  majority and the floor-auditor triages the tail.
- **Done is gate-defined** (never self-declared): every mirror `.py` stub is either a verified body
  or floor-audited into F1/F2/F3, the `wc -l` count is at the floor, and all gates are green.

The precise `(U,L)` pairs, barriers, gates A/B/C, loop steps, and the floor denylist are encoded
machine-readably in `config/skills/self-tcb-reduction/self-tcb-reduction.json`.

---

## 10. Execution log

### Iteration 1 (2026-07-03) — T1.a E-1 structural prerequisite LANDED; read-only handlers escalated

- **Starting count:** 1291 `\trusted`.
- **Delegated:** the 3 read-only expression handlers (`_handle_var_expr`, `_handle_field_get_expr`,
  `_handle_attribute_expr`), per the execution order.
- **Converter:** ported all 3 verbatim; the type-safety plane surfaced `unbound type symbol
  emit_ir` — the mirror's `ExpressionEmissionMixin` was not `@mutable_state`, so the emit_ir ADT
  theory never fired (the **CF0 analog** for the expression tier).
- **E-1 structural prerequisite (LANDED):** marked `ExpressionEmissionMixin` `@mutable_state
  @dataclass`, declared the state fields the expression handlers read, and added the
  `_add_abstract_op` / `_is_emit_ir_expr` sibling stubs. `expressions.py` now emits the emit_ir
  theory and **type-checks AND PROVES** with the marker in place; emitter (`src/pycsl`) untouched →
  **byte-diff 0 by construction**; mirror-sync green (24 verbatim).
- **Triage finding (escalation):** all 3 read-only handlers are the **needs-recognizer** class, not
  trivial leaves — each reflects on `node` (an `emit_ir`), so a ported body leaks `int` vs
  `emit_ir` on its first `node.get(...)`/`object_of` local (e.g. `obj_ir := object_of node` needs
  the emit_ir-local recognizer). Per **escalate-don't-thrash**, the per-handler conversions are
  flagged for a focused arc (the same multi-pass character as the statement-handler campaign), NOT
  ground on at the end of a long session.
- **Count after:** 1291 (unchanged — E-1 is a prerequisite; 0 stubs converted). Tree green.
- **Next:** convert the read-only handlers on the now-ready `@mutable_state` expression mixin,
  starting with `_handle_var_expr` (drive the `int`↔`emit_ir` local recognizers the way the
  statement handlers did), then the rest of T1.a.

### Iteration 2 (2026-07-03) — KEYSTONE recognizer LANDED (IR-node param → emit_ir); var escalated

- **Delegated:** `_handle_var_expr`. Ported verbatim; type-safety plane surfaced `name_of node`
  leaking — the `node: "ExprIR"` **param** was typed `int`, not `emit_ir`.
- **Keystone recognizer (LANDED, byte-diff 0):** an IR-node-typed PARAM (`node: "ExprIR"`,
  `stmt: "StmtIR"`, …) now resolves to `emit_ir` — in the symbol table
  (`Module5_IREmitter._build_function_symbol_table` via `_irnode_ann_name`) AND in the signature
  (`functions._param_type_str`, mirroring `_symtype_to_whyml`). Byte-safe: no corpus method
  annotates a param with the IR-node base names. **This unblocks the `node` param of ALL 24
  expression handlers at once** — the #1 blocker for the whole tier.
- **Escalation:** `var` additionally needs an Optional-`Dict[str,str]`-param + string-map
  membership recognizer cluster (`if subst and name in subst: name = subst[name]`), plus its
  remaining body — a full multi-recognizer cascade past this iteration's budget. Reverted `var` to
  a stub; flagged for the next pass.
- **Count after:** 1294 (unchanged — keystone is emitter infra; 0 stubs converted). Tree green,
  byte-diff 0.
- **Next:** convert `var` on the ready keystone (drive the Optional-dict-param + string-map
  recognizers), then `field_get`/`attribute`; the `node`-param blocker is now gone for all.

### Iteration 3 (2026-07-03) — KEYSTONE-2 (Optional[Dict] param → map) + map-truthiness; var progressing

- **Delegated:** `_handle_var_expr` again (on the ready IR-node-param keystone).
- **Keystone-2 (LANDED, byte-diff 0):** an `Optional[Dict[K,V]]` param is now modeled as the
  `Dict[K,V]` (None ≡ empty map) — `Module5._build_function_symbol_table` desugars it before the
  Union synthesis, so `subst: Optional[Dict[str,str]]` → `map string (option string)` and
  `name in subst` / `subst[name]` type as string-map ops. Byte-safe: 0 corpus methods have an
  `Optional[Dict]` param. **Unblocks the `subst` param of every reflecting expression handler.**
- **map-truthiness recognizer (byte-diff 0):** `if subst:` on a dict/set param → `true` (the
  present-guard before `name in subst`; a sound over-approx for type-safety+frame). @mutable_state.
- **var status:** most of the body now lowers cleanly (name_of, the membership ladder over
  `_array_locals`/`_lambda_locals`/…, module-constant reads); the remaining leak is the
  `_todict_aliases` branch's `for _p in _parts[1:]` loop over a `seq string` split — the seq-string
  iteration recognizer (same family as CF5) is the next per-handler fix.
- **Count after:** 1294 (unchanged — keystones are emitter infra; var not yet fully lowered). Tree
  green, byte-diff 0.
- **Next:** finish var's seq-parts-loop, land the FIRST expression-handler conversion (count →
  1293), then the passthrough-subst handlers become quick.

### Iteration 4 (2026-07-03) — seq-slice iterable recognizer + _expr_to_whyml stub sig; var 95%

- **Delegated:** `_handle_var_expr` (continuing).
- **seq-slice iterable recognizer (LANDED, byte-diff 0):** `for _p in _parts[1:]` where
  `_parts = s.split(".")` (a `seq string`) now iterates via `Seq.length`/`Seq.get` — a slice/
  subscript of a `seq` local is a seq (`_classify_iterable`, @mutable_state-gated). Byte-safe.
- **stub signature fix:** the mirror `_expr_to_whyml` stub's `local_refs`/`subst` params retyped
  `Set[str]`/`Optional[Dict[str,str]]` so the abstract self-call val accepts what the reflecting
  handlers pass (map-typed `subst`).
- **var status:** now lowers through the todict-alias parts loop; the ONE remaining leak is the
  niche module-constant branch `if type(val) == str: return '"' + val.replace(".","_") + '"'` —
  `_module_constants` is int-valued (`map int (option int)`), so `val.replace(...)` doesn't type as
  a string op. Needs module-constant value-typing (or a string-literal-anchored concat coercion) —
  the next per-handler fix.
- **Count after:** 1294 (unchanged). Tree green, byte-diff 0. var is ~95% converted — one niche
  branch from the first count reduction.

### Iteration 5 (2026-07-03) — 🎉 FIRST CONVERSION: `_handle_unaryop_expr` (count 1294→1293)

- **Switch of target (per iter-4 note):** var's last leak needs `isinstance(_cv, str)` narrowing on
  an int-valued module-constant dict — a deeper typing feature. Switched to the genuinely simple
  `_handle_unaryop_expr` (only `_expr_to_whyml`/`op_translate`/`_to_bool` + field access).
- **E-2 structural prerequisite (LANDED):** the concrete-ExprIR-subclass handlers annotate
  `node: "UnaryOpExpr"` (a quoted forward-ref), unlike the base `node: "ExprIR"`. Two fixes:
  (a) import the 5 concrete subclasses used (`AtExpr`/`IfExprExpr`/`NamedExprExpr`/`OldExpr`/
  `UnaryOpExpr`) in the mirror so they register as records (fields `op`/`expr`); (b) a QUOTED
  IR-subclass forward-ref param now resolves to that record in `Module5` (byte-safe: the corpus has
  no quoted `*Expr`/`*Stmt` param). Plus the mirror `_to_bool` stub's `ir_expr` retyped `"ExprIR"`.
- **✅ `_handle_unaryop_expr` un-`\trusted` + PROVEN:** type-checks, full proof green, byte-diff 0
  across the 627-corpus, mirror-sync verbatim (25 methods). **Count 1294 → 1293 — the first stub
  converted to a verified body.**
- **Next:** the other 4 concrete-subclass handlers (`at`/`ifexpr`/`named_expr`/`old`) now inherit
  the E-2 record resolution — likely quick conversions; then return to the base-`ExprIR` handlers.

### Iteration 6 (2026-07-03) — 2 more conversions: `old` + `at` (count 1293→1291)

- A batch-port of the 4 remaining concrete-subclass handlers exposed a cross-handler interaction
  (`named_expr`/`ifexpr` perturbed an untouched sibling `_cf5_arr`) → reverted to strict per-stub
  discipline.
- **`.kind` emit_ir-attribute recognizer (LANDED, byte-diff 0):** `<emit_ir>.kind` is the
  DISCRIMINANT string (`kind_of`), not a sub-node — fixed both the lowering
  (`_handle_attribute_expr`: `attr == "kind"` → `kind_of`) and the typing (`_is_string_expr`:
  `<emit_ir>.kind` → string, so `inner.kind == "Subscript"` routes through `str_eq_op`).
  @mutable_state-gated.
- **✅ `_handle_old_expr` + `_handle_at_expr` un-`\trusted` + PROVEN:** type-check, full proof green,
  byte-diff 0, mirror-sync verbatim (27 methods). **Count 1293 → 1291.**
- **Next:** `named_expr`/`ifexpr` (investigate the `_cf5_arr` cross-interaction), then the
  base-`ExprIR` handlers (`arraylen`/`slice_access`/…) and back to var's tail.

### Iteration 7 (2026-07-03) — `named_expr` converts (1291→1290); `ifexpr` escalated

- **`_handle_named_expr_expr` un-`\trusted` + PROVEN** on the accumulated recognizers — NO new
  emitter change needed (byte-diff 0 by construction), mirror-sync verbatim (28 methods).
  **Count 1291 → 1290.**
- **`ifexpr` ESCALATED:** porting `_handle_ifexpr_expr` reproducibly breaks an UNTOUCHED sibling
  `_cf5_arr` (its `d.get("name") == …` reverts to an int-hash compare instead of `str_eq_op`) — a
  genuine cross-method interaction, not a per-handler leak. Flagged for a focused diagnostic pass;
  reverted to a stub to keep the tree green.
- **Next:** diagnose `ifexpr → _cf5_arr`; meanwhile convert base-`ExprIR` handlers.

### Iteration 8 (2026-07-03) — general infra: `_EMIT_IR_STR_ATTRS` map + 5 fields; arraylen escalated

- **`_EMIT_IR_STR_ATTRS` recognizer (LANDED, byte-diff 0):** generalized the `.kind` fix into a map
  of STRING-valued emit_ir attributes (`kind`→`kind_of`, `var`/`op`/`label`/`name`→`name_of`,
  `func`→`func_of`) for base-`ExprIR`-annotated nodes accessing a concrete subclass's str field.
  Both the lowering (`_handle_attribute_expr`) and typing (`_is_string_expr`). @mutable_state.
- **5 more mixin fields declared:** `_in_spec`/`_value_semantic`/`_seq_locals`/`_result_alias`/
  `_heap_var` (the E-1 field set grows as handlers surface reads).
- **arraylen ESCALATED:** `var in getattr(self, "_seq_locals", set())` — the getattr-defensive
  set-membership does NOT hash the string key (`Map.get _seq_locals !var` vs the direct-field form's
  `str_hash_op`), so a string key hits an int-keyed map. A general getattr-set-membership recognizer
  is the next fix (unblocks arraylen + others). Reverted to stub; tree green, byte-diff 0.
- **Count after:** 1290 (infra iteration; no conversion). Tree green.

### Iteration 9 (2026-07-03) — 2 general recognizers (getattr-set membership + string-local typing)

- **getattr-set-membership hash (LANDED, byte-diff 0):** `x in getattr(self, "_set_field", set())`
  now fires the `str_hash_op` key-hash for SET self-fields (not only dict fields) — mirrors the
  direct `x in self._set_field` path. Unblocks the defensive-`in getattr(...)` idiom used across
  many handlers.
- **`_string_local_vars` in `_is_string_expr(Var)` (LANDED, byte-diff 0):** a collected string
  LOCAL (`var = node.var` → name_of) now counts as string in membership/concat even before its
  symbol-table type is set. Byte-safe (empty outside @mutable_state).
- **arraylen further:** the seq/array-locals membership + `var` string-typing now lower; the next
  leak is `field = var[len("self."):]` (a string SLICE local not yet collected as string in the
  `f"self.{field}"` interpolation).
- **Count after:** 1290 (2nd consecutive infra iteration; recognizers unblock the base-`ExprIR`
  handlers). Tree green, byte-diff 0.
- **Note:** to resume conversions, next iteration will try a handler the accumulated recognizers
  already convert (or finish arraylen's string-slice-local), rather than keep drilling one handler.

### Iteration 10 (2026-07-03) — 🎉 4 conversions (spec handlers) via `base`→name_of (1290→1286)

- **Pivot (per iter-9 note):** stopped drilling arraylen; auto-tried the base-`ExprIR` handlers to
  find which the accumulated recognizers already convert. Adding ONE map entry — `base` → `name_of`
  to `_EMIT_IR_STR_ATTRS` — unblocked FOUR at once (they all read `node.base`).
- **✅ `issorted` + `length2d` + `valid` + `valid2d` un-`\trusted` + PROVEN:** type-check, full
  proof green, byte-diff 0, mirror-sync verbatim (32 methods). **Count 1290 → 1286.**
- This validates the pivot strategy: once the shared recognizers accumulate, a single new entry
  cashes out across a whole family of handlers. `separated` still leaks (own recognizer next).
- **Total this run:** 8 handlers converted (unaryop/old/at/named_expr/issorted/length2d/valid/
  valid2d), count 1294 → 1286.

### Iteration 11 (2026-07-03) — auto-try harvests 4 more: arrayeq/permutation/sum_node/lambda (1286→1282)

- Built a reusable **auto-try harness** (`/tmp/autotry.py`): ports each trusted handler, type-checks,
  KEEPs it if green else reverts + captures the first leak. Ran it over all remaining trusted
  `_handle_*_expr`.
- **✅ 4 convert with ZERO new emitter change** (on the accumulated recognizers): `arrayeq`,
  `permutation`, `sum_node`, `lambda` — un-`\trusted` + PROVEN, byte-diff 0 by construction,
  mirror-sync verbatim (36 methods). **Count 1286 → 1282.**
- **Leak map captured for the rest** (the next recognizer targets): `in_globals`/`in_scope`
  (`name in <method-result>` string-membership), `field_get` (`_field_label` str arg), `arraylen`
  (field-slice), `var` (module-const str branch), `fstring`/`slice_access`/`attribute`/`call`/
  `separated` (emit_ir/args reflection), `ifexpr` (`_cf5_arr` interaction).
- **Total this run: 12 handlers converted, count 1294 → 1282.**

### Iteration 12 (2026-07-03) — in_scope + in_globals (1282→1280)

- **in_scope:** declared its scope fields (`_scope_must`/`_scope_all`/`_scope_params`/
  `_scope_dyn_exec`) → the iteration-9 getattr-set-membership recognizer hashed the keys. Converted.
- **method-call-set membership recognizer (LANDED, byte-diff 0):** `x in self._method()` where the
  method returns `Set[str]`/`dict` (`name in self._module_binding_names()`) → map membership. Plus
  retyped the `_module_binding_names` stub `Set[str]`. Converted `in_globals`.
- **✅ `in_scope` + `in_globals` un-`\trusted` + PROVEN:** full proof green, byte-diff 0, mirror-sync
  verbatim (38 methods). **Count 1282 → 1280.**
- **Total this run: 14 handlers converted, count 1294 → 1280.**

### Iteration 13 (2026-07-03) — node-LIST-attr recognizers → setlit converts (1280→1279)

- **`_field_label` stub `record_lower` retyped `str`** (was Optional[str]-collapsed).
- **node-LIST attribute recognizers (LANDED, byte-diff 0):** `node.elts`/`node.parts`/`node.args`/
  `node.captures` (a node-list attr on a base-`ExprIR` node) → `args_of` (`array emit_ir`), across
  four sites: the lowering (`_handle_attribute_expr`), the array-var collector (`x = node.elts` →
  array local), the elem-type collector (→ emit_ir element), AND crucially `_is_emit_ir_expr` now
  EXCLUDES these list-attrs (they are arrays, not scalar sub-nodes — was mis-declaring `elts`
  as `ref (IrOther "")`). @mutable_state-gated.
- **✅ `_handle_setlit_expr` un-`\trusted` + PROVEN** (39 methods verbatim). **Count 1280 → 1279.**
- `fstring` uses the same `node.parts` but has a further leak (next). field_get/var/ifexpr remain
  escalated (object-as-string / module-const-string / _cf5_arr).
- **Total this run: 15 handlers converted, count 1294 → 1279.**

### Iteration 14 (2026-07-03) — `.get`-form node-list recognizers banked; fstring escalated

- **`.get("parts"/"elts")` node-list recognizers (LANDED, byte-diff 0, PROVEN):** extended the
  iteration-13 node-list handling from the attribute form to the `.get` form —
  `_EMIT_IR_PROJ["parts"/"elts"] = args_of`, the array-var collector `.get` key lists, and
  `_val_elem_ty`'s `.get` keys now include `parts`/`elts`. General infra for `x = expr.get("elts")`.
- **fstring ESCALATED — important process finding:** the auto-try `--no-proof` check
  **false-positived** on fstring (reported convert), but the FULL proof caught a type error in
  proof mode — its nested `_sp` helper + `parts[0]` (emit_ir element) types differently under proof
  than under `--no-proof`. The proof gate correctly blocked the bad commit. **Lesson: `--no-proof`
  ≠ proof type-check for nested-function constructs; the full-proof gate before commit is
  load-bearing, not redundant.** fstring reverted; needs the nested-`_sp` recognizer next.
- **Count after:** 1279 (no new conversion; infra + a false-positive caught). Tree green, PROVEN,
  byte-diff 0.
