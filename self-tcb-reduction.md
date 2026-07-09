# self-tcb-reduction.md — shrink the self-annotation trusted core toward its irreducible floor

> ## 📍 ROLE / HIERARCHY (read first)
> **This is NOT the current strategic plan.** The **plan of record is `triage-ranked-tcb.md`** — the
> empirically-calibrated go-forward plan (tier ranking, calibrations, closure). This document's live role
> is now twofold: (a) the **SL loop procedure** (paired with `config/skills/self-tcb-reduction/SKILL.md`,
> incl. the §5.1 streamlined gate), and (b) the **append-only §8 iteration ledger** (the execution log).
> For strategy, direction, and "what's next," read `triage-ranked-tcb.md`; append iteration entries here.
>
> **Campaign status (2026-07-06): CLOSED at count 1240.** Tiers 1/2/3 all executed and closed at their
> honest floors (marker yields **8 / 0 / 9**); the certified tier-3 ADT foundation is banked. The prose
> below is the original long-horizon framing — historical; read it through this banner and the plan of
> record. **Next work (NOT planned here):** the **141 trusted-pending** stubs, blocked by separate
> value-model gaps (85 `Dict[str,Any]` value-typing + 43 collection-result modeling + 13 emitter
> string/self-state) — a distinct, demand-driven effort outside the ADT campaign
> (see `getting-better/tier3/whole-body-census.md` + `step-d-leave-trusted-analysis.md`).

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

### Iteration 2026-07-05 — TIER-1 trivial-leaf batch (streamlined gate §5.1)

Batch-converted the triage-ranked TIER-1 "free win" trivial-leaf stubs. Global `\trusted` grep
count **1260 → 1252** (net **8** converted, all mirror-only, byte-diff 0 by construction —
`src/pycsl` emitter + corpus BYTE-IDENTICAL to baseline `961c89f9`). No emitter file touched; no
axiom / allowlist change.

**Converted (8, each proven — fidelity + full-file Why3 discharge, or `--fun` for the two big
files):**
- `proof2why3/crosscheck.py` — `_module_namespace_of` (const-string) — 8→7
- `frontend/Module2_Parser.py` — `__init__` (rdp-compat `pass`) — 91→90
- `frontend/Module1_Ingestor.py` — `_clean` (string slice+strip) — 18→17
- `frontend/ir_inline.py` — `_method_key` (all-string f-string) — 17→16
- `Module6_WhyMLTranspiler.py` — `_wrap_unannotated_call_with_strict_assert` — 22→21
- `proof2why3/ir.py` — `Var.pp` (`return self.name`), `Unsupported.pp` (f-string over str field);
  frozen `@dataclass` fields DO render as `string` record fields — 13→11
- `module6_whyml/stmt_control_flow.py` — `_union_arm_whyml_type` (string-dict `.get`) — 23→22

**Reclassified non-trivial / proof-not-free (deferred, `\trusted` restored):**
- `module6_whyml/ir_scanner.py` — **all 18** candidates. `uses_inline_set_or_dict_ops` = typecheck
  fail (`obj.values()` → int/array mismatch). The 17 recursive IR-tree walkers: **13 discharge in
  per-function `--fun` isolation** but the **full-file gate FAILS** — Alt-Ergo times out (30 s/goal)
  on the postcondition / array-creation VCs of the recursive-scanner set in the COMBINED file
  context; even a 13-only subset full-file proof times out. `--no-proof` (typecheck-only, the triage
  probe's basis) was too weak an oracle here. Proof-not-free: needs a per-goal-timeout bump or a
  recursion lemma, out of tier-1 scope.
- `module6_whyml/expr_ghost_collections.py` — 3 const-string handlers
  (`_handle_map_empty/set_empty/nil_expr`): live signature `node: "ExprIR"` lowers to `unbound type
  symbol 'emit_ir'` standalone (sync forbids changing the def line). Gated on the emit_ir ADT.
- `module6_whyml/types.py` — `_val_is_bool`, `_bool_ir_to_int_wrap`: explicit `Dict[str, Any]`
  param triggers the faithful `map string (option int)` model; `.get("type")` → `option int`
  mismatches the string-literal comparisons (`is None` also mismatches on a map). Value-model gap.
- `module6_whyml/functions.py` — `_symtype_to_whyml`: `Optional[str]` + tuple-membership emits a
  `_union__…` type that mismatches the string return.
- `proof2why3/ir.py` — `BoolLit.pp`: `bool` record field ITE → int/string type mismatch.
- `module6_whyml/stmt_control_flow.py` — `_try_local_decl_kind` (Dict-param map model + self-field);
  the 4 nominal candidates (`_materialize_bridge`, `_materialize_str_bridge`, `_bool_ir_to_int_wrap`,
  `_coerce_to_int`) are **mirror-only** (no live counterpart in `stmt_control_flow.py` — the real
  leaf is the sibling home file), so converting them here would earn NO fidelity guarantee — skipped.

**Batch confirmation:** fidelity (`check-self-annotate-sync.sh`) green; byte-diff 0 by construction
(emitter+corpus unchanged vs baseline); full `run-self-annotation-suite.sh` — no NEW failure vs the
known pre-existing set. Commits: `3400ceef e88026c8 f556927b 47464411 19417433 5671455e 281ab3ec`.

**Definition of done.** Every `.py` stub in the mirror is either (a) a verified body or (b)
enumerated in the F1/F3 audited floor with a reason; the `wc -l` trusted count is reduced to that
floor; `check-self-annotate-sync.sh`, `self-annotate-mirror-check.sh`, and
`run-self-annotation-suite.sh` all green; byte-diff 0 throughout.

### Iteration 2026-07-06 — TIER-3-v2 PATH-1 harvest (census `whole-body-census.md` §5 PATH 1)

Harvested the census-confirmed **convertible-NOW** `\trusted` stubs — the bounded, zero-build,
no-new-axiom conversion the tier3-v2 whole-body census (`getting-better/tier3/whole-body-census.md`)
recommends as the honest floor. Global canonical `\trusted` count **1249 → 1240** (net **9**
converted, all in `ir_scanner.py`, mirror-only). `src/pycsl` emitter untouched (byte-diff 0 by
construction); `why3-semantics` untouched; `proof_axiom_allowlist` unchanged.

**Converted (9, each proven whole-body via per-function `--fun` — safety + termination +
non-vacuity; live body ported verbatim, fixed contract `requires True`/`ensures True`/`assigns
\nothing`, `\trusted` marker removed):**
- `module6_whyml/ir_scanner.py` — `uses_subscript`, `uses_array_lit`, `uses_minmax`,
  `is_recursive`, `uses_string`, `uses_sum`, `uses_set_card`, `uses_ord_chr`, `uses_divmod`
  (the 9 substantive reflective IR-tree predicate walkers). Each `irscanner__<name>` reaches
  `Verification SUCCESS` under `pycsl.py … --fun <name>`. The combined-file gate does NOT time out
  here — `ir_scanner.py` **PASSES the full-file suite proof** (superseding the 2026-07-05 deferral,
  which had `uses_inline_set_or_dict_ops` — a typecheck-failer — in the batch).

**Census discrepancies (2 of the "11" did NOT reproduce — NOT forced, per the non-vacuity guard):**
- `statements.py::_wrap_body_with_return_catch` — census listed it convertible-NOW, but on disk it
  is **already un-`\trusted`** with the full live body (not a stub); converting it is a no-op and it
  is **not** in the 1249 count. (It also currently FAILS the full-file statements.py proof on the
  f-string-hash→int limitation — a pre-existing state independent of this harvest.)
- `expressions.py::_e` — census listed it convertible-NOW, but with the live body
  (`return self._expr_to_whyml(ir, lr)`) it **FAILS** `--fun` in the committed mirror: the trusted
  `_expr_to_whyml` stub's declared return type mismatches (`type int … expected PyCSL_Program.emit_ir`).
  The census probe passed only because `sync-mirror-bodies.py` also ports every sibling's signature/
  return-type; a pure single-method edit does not. Left `\trusted` (reverted).

So the measured harvest yield is **9, not 11** (target 1238 → actual **1240**).

**Batch confirmation:** fidelity (`check-self-annotate-sync.sh` — 90 un-trusted mirror fns verbatim;
`self-annotate-mirror-check.sh` — 51 mirrors in sync) green; byte-diff 0 by construction
(`src/pycsl` byte-identical to baseline `7a750917`); `run-self-annotation-suite.sh` — the only file
this iteration touched, `ir_scanner.py`, **PASSES**; the pre-existing FAIL set (`pycsl.py`,
`expressions.py`, `statements.py`, …) is byte-identical to `7a750917` (no NEW failure). Commit:
`7e398d4e`.

**Marker campaign closed at the honest floor** per the census: the ADT-relevant convertible-NOW
frontier is now exhausted (9 harvested; `_wrap` already-converted; `_e` census-non-reproducing).
Residual = **141 semantic-ceiling other-blockers** (85 `Dict[str,Any]` value-typing + 43
collection-result modeling + 13 emitter string/self-state/WhyML-gen) **+ 2 leave-trusted**
(`find_named_expr_targets`, `_collect_assign_targets` — by-ref dict/set param mutation, PyCSL
rejects at the pipeline, fail-stop) — all outside the IR-node ADT's reach without a live-source
rewrite.

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

### Iteration 15 (2026-07-03) — separated converts via base1/base2→name_of (1279→1278)

- **Probed the helper files** (identifiers/scc/…): they are a DIFFERENT verification domain
  (module-level functions, not @mutable_state methods) where the gated recognizers don't fire and
  un-gating risks byte-diff — so they're NOT the easy wins they looked like. Reverted; stayed in
  the @mutable_state expr-handler domain.
- **`base1`/`base2` → name_of (LANDED, byte-diff 0):** two more array-name fields added to
  `_EMIT_IR_STR_ATTRS` (like `base`).
- **✅ `_handle_separated_expr` un-`\trusted` + PROVEN** (full proof, not just --no-proof — per the
  iter-14 lesson), byte-diff 0, mirror-sync verbatim (40 methods). **Count 1279 → 1278.**
- **Total this run: 16 handlers converted, count 1294 → 1278.**

### Iteration 16 (2026-07-03) — ESCALATION CHECKPOINT: T1.a tractable tail exhausted (stays 1278)

Attempted `slice_access` (77 lines) — the emit_ir-truthiness recognizer (`if sl.get("lower")` →
`true`) landed but the handler kept cascading into deep reflection semantics (`sl["lower"]` =
subscript-on-emit_ir returning the wrong type). Per **escalate-don't-thrash** (attempt budget),
reverted it AND the orphaned recognizer (no converting consumer). Probed the rest by size/blocker.

**All 7 remaining T1.a `_handle_*_expr` are hard-architectural — flagged for a focused
high-reasoning pass, NOT the 1-minute incremental loop:**

| Handler | Lines | Blocker (needs a focused pass) |
|---------|-------|--------------------------------|
| `_handle_field_get_expr` | 23 | **object-as-string ambiguity**: `FieldGet.object` is a str (name), `Attribute.object` is a sub-node — same `"object"` key, node-type-dependent projection the flat emit_ir model can't distinguish |
| `_handle_var_expr` | 63 | **union-narrowing**: `_module_constants[name]` values are `Union[str,int]`; the `isinstance(_cv,str)` branch + `.replace` escaping needs value-narrowing the int-collapsed map lacks |
| `_handle_attribute_expr` | 66 | deep `object`/`attr` reflection + per-node-type projection |
| `_handle_slice_access_expr` | 77 | subscript-on-emit_ir (`sl["lower"]`) reflection semantics returning wrong element type |
| `_handle_call_expr` | 285 | **the giant** — full args_of/func reflection across every call shape |
| `_handle_fstring_expr` | ~55 | nested `_sp` helper types `parts[0]` differently under proof mode (iter-14) |
| `_handle_ifexpr_expr` | ~40 | cross-method `_cf5_arr` interaction (iter-7) |

**Verdict:** the tractable T1.a tail (16 handlers: unaryop/old/at/named_expr/issorted/length2d/
valid/valid2d/arrayeq/permutation/sum_node/lambda/in_scope/in_globals/setlit/separated) is
**complete** — count **1294 → 1278**. The remaining 7 share NO cheap recognizer; each needs a
dedicated reflection/narrowing feature (a `Plan`/high-reasoning pass), which is the loop's
escalation target, not incremental grinding. Tree green, byte-diff 0, PROVEN at 1278.

---

## Execution Status — 2026-07-03 (this run)

**Result: `\trusted` count 1294 → 1278 (16 T1.a expression handlers converted), every increment
PROVEN + byte-diff 0 + mirror-sync verbatim.** The tractable T1.a tail is complete.

**Converted (16):** unaryop, old, at, named_expr, issorted, length2d, valid, valid2d, arrayeq,
permutation, sum_node, lambda, in_scope, in_globals, setlit, separated.

**Recognizer foundation banked** (all `@mutable_state`/emit_ir-gated, byte-diff 0): IR-node params →
emit_ir; `_EMIT_IR_STR_ATTRS` (kind/var/op/label/name/func/base/base1/base2 → discriminant/name
projections); node-LIST attrs (elts/parts/args/captures → `args_of`, across lowering + array-var +
elem-type collectors + the `_is_emit_ir_expr` scalar-exclusion, both attribute AND `.get` forms);
getattr-set-membership `str_hash_op` for set fields; method-call-set membership; `_string_local_vars`
in `_is_string_expr`; ~25 mirror state-field declarations.

**Remaining 7 = hard-architectural (flagged for a dedicated high-reasoning / `Plan` pass — see the
iteration-16 table).** Each needs a real modeling feature, NOT a recognizer:
- `field_get` — CONFIRMED via focused pass: `expr['object']` must yield the object *name string*,
  but emit_ir stores object as a *node* (`object_of`); the real IR (`FieldGet.object: str`) and the
  flat emit_ir model disagree on this field's type. Needs a FieldGet-specific object-name projection
  (`name_of ∘ object_of`, or a dedicated `objname_of`), distinct from `Attribute.object` (a node).
- `var` — `_module_constants` values are `Union[str,int]`; needs value-narrowing (isinstance) the
  int-collapse lacks.
- `attribute` / `slice_access` / `call` (285L) — deep object/args/subscript-on-emit_ir reflection.
- `fstring` — nested `_sp` helper types `parts[0]` differently under proof mode.
- `ifexpr` — cross-method `_cf5_arr` interaction.

**Process finding (iter-14):** the auto-try `--no-proof` check can FALSE-POSITIVE on nested-function
constructs; the full-proof gate before commit is load-bearing, not redundant.

**Clean stopping point.** Tree green at 1278; ready for a future dedicated session on the hard tail
(recommend starting with `field_get`'s object-name projection — smallest, fully diagnosed above).

### Iteration 17 (2026-07-03) — field_get object-name projection LANDED; nested-dict is the sole remaining blocker

- **subscript-`['object']` → object NAME (LANDED, byte-diff 0, PROVEN):** the focused pass on
  field_get's first blocker. `expr['object']` (subscript) now lowers to `name_of (object_of node)`
  (the object's name string), disambiguated from `.get("object")` (a node) by access form — the same
  device as `pattern`. Both un-trusted subscript-`object` users read it as a string, so this is a
  faithfulness FIX (the old subscript-`object`→node was semantically wrong). Coordinated across the
  lowering (`_handle_subscript`), `_is_emit_ir_expr` (exclude), and `_is_string_expr` (include).
- **field_get's SECOND blocker isolated — nested-dict:** `_class_constants: Dict[str, Dict[str,int]]`
  flattens to `map int (option int)`, so `field in self._class_constants.get(self_type, {})` +
  the double-subscript `self._class_constants[self_type][field]` need a NESTED-map model the
  int-collapse lacks. This is field_get's only remaining blocker (a real feature, not a recognizer).
- field_get reverted to stub; tree PROVEN at 1278, byte-diff 0, 40 methods verbatim. The object-name
  projection is banked (correctness + de-risks the eventual field_get conversion to a single feature).

### Iteration 18 (2026-07-03) — nested-dict feasibility CONFIRMED not expressible (stays 1278)

Experiment: declared `_class_constants: Dict[str, Dict[str, int]]` (proper nested type) + ported
field_get. Result: **identical leak** (`'mu -> option int` @ the `.get(self_type, {})` membership) —
the field-type system **flattens `Dict[str, Dict]` → `map int (option int)`**, losing the inner
structure, so `_class_constants[self_type][field]` (double-subscript) and `field in …get(…)` cannot
type-check. Even an opaque-inner recognizer needs the type system to KNOW the field is nested, which
it discards. **Verdict: field_get's remaining blocker is a genuine nested-map feature in the
field-type system — a demand-driven feature warranting an SMT-feasibility spike, NOT a loop
recognizer.** Experiment reverted; tree green at 1278.

---

## Loop yield assessment (after 18 iterations)

- **Conversions: 16 handlers, 1294 → 1278** (iterations 5–15). The tractable T1.a tail is done.
- **Iterations 16–18 yielded diagnoses + one correctness fix, ZERO conversions** — each remaining
  handler's blocker was precisely characterized as a dedicated feature:
  - `field_get` → nested-map field type (CONFIRMED not expressible today) + object-name (SOLVED).
  - `var` → `Union[str,int]` value-narrowing.
  - `attribute`/`slice_access`/`call` → deep object/args/subscript-on-emit_ir reflection.
  - `fstring` → nested-`_sp` proof-mode typing.
  - `ifexpr` → cross-method `_cf5_arr` interaction.
- **Conclusion:** the 1-minute incremental loop has exhausted its conversion yield. Each further
  handler needs a demand-driven modeling feature (spike → implement → gate), which is focused
  feature work, not loop iteration. **Recommend switching modes** (build one named feature, e.g.
  nested-map, on request) rather than continuing blind relaunch.

### Iteration 19 (2026-07-03) — 🎯 NESTED-MAP FEATURE → field_get CONVERTS (1278→1277)

The demand-driven feature (field_get = driver) that iteration 18 found necessary. **SMT spike first**
(hand-written nested-map `.mlw`, `double_subscript` Valid 0.04s → Why3 handles nested maps trivially;
the work is pipeline). Then 6 coordinated pipeline edits, all byte-diff 0 (corpus has no nested-dict
field → inert) + PROVEN:
1. **Module5 `_m5_get_dict_value_type`:** inner map is int-keyed (`map int (option _)`, str keys
   hashed) — uniform with the model's `dict[str,_] ~ map int` convention (was `map string`).
2. **preamble field-type:** a nested collection value (`value_type` starts `map`/`seq`/`array`) is
   preserved as `map int (option (<inner>))`, not flattened to `option int`.
3. **membership:** `k in self._nested.get(k1, {})` → the `.get` returns the inner map → map
   membership (hash the key).
4. **subscript default:** a nested-dict field read's missing-key default is the empty inner map
   (`const None`), not int `0`.
5. **nested subscript handler:** extended the body-dict `d[ko][ki]` case to a self-field inner base
   (`self._nested[ko][ki]`).
6. **inner-key hash:** the inner `[ki]` hashes a string key into the int-keyed inner map.
- **✅ `_handle_field_get_expr` un-`\trusted` + PROVEN** — a FIRST hard-architectural handler
  converted via a real modeling feature, not a recognizer. **Count 1278 → 1277.**
- **Total: 17 handlers converted, count 1294 → 1277.** Remaining hard tail: var, attribute,
  slice_access, call, fstring, ifexpr (each still needs its own feature).

**Nested-map scope note (iter-19):** the feature is PROVEN on the emitter mirror (field_get's
`_class_constants`, a @mutable_state/@dataclass field). A plain-class corpus reference test (0746,
drafted) surfaced that a plain class's nested-dict field value_type is not extracted the same way
(the field lowers flat `map int (option int)` while the membership fix assumes nested) — a separate
plain-class field-collection generalization. Deferred (mirror proof is the validation); the corpus
reference test lands with that generalization. Core field_get conversion is unaffected (proven,
byte-diff 0).

### Iteration 20 (2026-07-03) — var union-narrowing SOLVED, but var blocked on a separate issue (stays 1277)

Attempted `_handle_var_expr` (63 lines). The NAMED blocker — **union-narrowing SOLVED**:
- `_module_constants` values are `Union[str,int]` (`_cv.replace(...)` string branch vs `f"({_cv})"`
  int branch). Sound model: declare the value type `str` — then `isinstance(_cv, str)` is always-true,
  the string branch type-checks, and the (dead) int branch's `f"({_cv})"` is string interpolation.
  The `replace_2`-on-int leak is GONE. (+ declared the missing `_variant_types` field.)

But var has a SECOND, independent blocker that is NOT union-narrowing — **a for-loop-over-seq-slice
variant in a LOGIC context**:
- var's `_todict_aliases` branch does `_parts = _al.split("."); for _p in _parts[1:]: …`. The slice
  loop's `variant { (Seq.length (seq_sub _parts 1 0)) - _idx }` references `seq_sub`, which is a
  program `val` (registered fine, declared at module top) — but a `variant {}` is a **logic** term,
  where a program `val` is unbound. Fixing it via a logic `function seq_sub` + length axiom would
  **smuggle an axiom** (against the no-added-axiom discipline); the clean fix is a logic-safe loop
  variant for seq-slice loops (use the base seq's `Seq.length`, a pure logic fn) — a for-loop-variant
  feature, separate from union-narrowing.
- Reverted the attempt to clean 1277. **Union-narrowing modeling is proven correct** (the leak it
  targets is gone); var's conversion waits on the seq-slice-variant fix.
- **Count stays 1277 (17 converted).** The val-vs-logic seq-slice-variant issue is the same class as
  fstring's nested-`_sp` — a logic-context constraint the loop's recognizers can't cross.

### Iteration 21 (2026-07-05) — fidelity plane REPAIRED (drift resync); T1.b helper leaf frontier = feature-gated

**E-0 baseline** pinned from committed HEAD (746-file byte-diff sweep, /tmp/sltcb_baseline). Start
count **1262**.

**Fidelity plane was RED at HEAD.** `check-self-annotate-sync.sh` exited 1: one DIVERGED method,
`statements.py::_handle_array_set_stmt` — the live emitter grew the WL-04f nested-inner-mutation
branch (`a[i][j]=v -> a[i] <- Seq.set a[i] j v`, non-int-leaf nested lists) in the recent WL-04/WL-06
commits, but the mirror's un-trusted copy was never resynced. This blocked the fidelity plane
tree-wide (Gate B unreachable for ANY conversion). **RESYNCED** (verbatim live-body port, commit
`4ef18975`): sync exit 1->0, byte-diff 0 (mirror-only, no src/pycsl change), count unchanged, no NEW
suite failure (statements.py had a pre-existing int/string type leak in the method's top guard,
orthogonal to the resync — it did not type-check at HEAD either).

**Triage probe** (parallel actor) classified the T1.b Module-6 helper leaves
(identifiers/scc/abstract_ops/struct_format/auto_trust/expr_ghost_spec_ops): 3 nominal TRIVIAL-LEAF,
the rest BLOCKED-SET / BLOCKED-RECURSION / BLOCKED-OTHER. **All 3 "trivial" leaves proved
feature-gated when actually run through pycsl** (the probe does not run pycsl):

- `identifiers::op_translate` (`return OP_MAP.get(op, op)`) -> FLAG-HARD. Missing feature:
  **module-level constant-dict `.get` recognizer**. The existing constant-dict recognizer is
  class-constant-only; a module constant lowers `.get` to an opaque `val oP_MAP_get_2 (int)(int):int`,
  so the string arg leaks (int expected). Reverted.
- `identifiers::safe_exc_name` (`return name.lstrip("_") or name`) -> FLAG-HARD. Missing feature:
  **string-valued `or`** (`str or str` returns a string in Python, not a bool; lowering treats it as
  boolean-or -> int leak) **+ faithful `.lstrip(arg)`** (arg dropped). Reverted.
- `struct_format::arity` (`return len(self.slots)`, `slots: List[str]`) -> FLAG-HARD. Missing feature:
  **`use array.Array` in the preamble for a NON-`@mutable_state` module with an array-typed record
  field** (`use array.Array` is currently forced only for `@mutable_state` modules; StructFormat is a
  frozen value dataclass, so its `array string` field leaks `unbound type symbol 'array'`). Reverted.

Everything else in T1.b helpers is a hard blocker: BLOCKED-SET (`find_calls_in_ir`,
`find_self_method_calls`, `sort_functions_by_scc`, `_advance_past_referenced_axiom_decls`,
`_insert_abstract_val_block`, `_collect_map_typed_locals` — set-local modeling still absent),
BLOCKED-RECURSION (`compute_sccs`, `_is_linear_expr`, `_test_contains_map`, `_has_set_op_on_map`,
`_should_auto_trust_tuple_return`), or external-callback-gated (all `expr_ghost_spec_ops` handlers
call still-`\trusted` `ExpressionEmissionMixin` methods `self._e`/`_deref`/`_expr_to_whyml_string_ctx`).

**End count 1262 (0 conversions).** byte-diff 0 held throughout; `proof_axiom_allowlist` unchanged; no
coherent-and-wrong caught (no conversion passed). **Verdict:** the in-stack-recognizer / byte-diff-0
STUB-port frontier is EXHAUSTED across T1.a (iters 16-20) AND now T1.b helper leaves — every remaining
leaf needs a demand-driven emitter FEATURE (spike->implement->gate), which is focused feature work, not
loop iteration. Per "escalate-not-thrash", flagged with exact missing features above; NOT ground on.
Next tractable pickup is smallest-feature-first: `module-level constant-dict .get` (unblocks
`op_translate`) or `use array.Array` preamble for value-record array fields (unblocks
`struct_format::arity`).

### Iteration 22 (2026-07-05) — 🎯 op_translate CONVERTS via module-const-dict-get feature (1262→1261)

The demand-driven feature flagged in iteration 21 (module-level constant str→str dict
`.get(k, default)`) LANDED (commit `69ea852e`): the pattern now lowers to a faithful chained string
if-then-else (11-arm ITE over the key), so the string arg no longer leaks to int. This iteration
converts the sole consumer, `identifiers::op_translate`, through the full SL loop.

- **converter:** ported the live body verbatim — `return OP_MAP.get(op, op)` (+ the live docstring);
  retyped the module constant `OP_MAP: Dict[str, str]` (was the stub placeholder `int`) so the
  recognizer fires. Contract shape `#@ requires True / ensures True / assigns \nothing` (type-safety +
  frame, non-value-faithful, non-vacuous). Local `--no-proof`: L3-tc ✓.
- **Gate A:** T1.b tier, not on floor denylist, contract shape correct → APPROVED; `\trusted` removed.
- **VERIFIER (fresh, surface-only) — three L planes, ALL PASS:**
  - **Fidelity:** `check-self-annotate-sync.sh` exit 0 (68 un-trusted mirror fns verbatim) ∧
    `self-annotate-mirror-check.sh` exit 0 (51 mirrors in sync).
  - **Type-safety:** `Verification SUCCESS` — op_translate postcondition Valid 0.01s via best-of-N
    **Z3** (the sanctioned string-theory path; Alt-Ergo has no string theory). `proof_axiom_allowlist`
    diff **EMPTY** (no smuggled axiom).
  - **Corpus inertness:** byte-diff **0** vs the re-pinned E-0 baseline (748 corpus files identical);
    suite **no NEW failure** (identifiers.py PASSES; the failed set — pycsl.py `_Directive`,
    expressions.py/statements.py int/string leaks, 7 unmirrored "file missing" — is a subset of the
    known pre-existing failures); `\trusted` count **1262 → 1261** (canonical `\\trusted` marker
    count; strict −1).
- **Gate B + Gate C:** all three planes pass, unblended; non-vacuity holds (tight `\nothing` frame,
  real verbatim body, genuine string-ITE postcondition discharge — not a stub). No coherent-and-wrong
  caught. Committed `c397dffe`.
- **Adjacent-leaf sweep:** the freed feature's exact pattern (`ALLCAPS_CONST.get(k, str_default)`) has
  **no other consumer** in the still-trusted frontier (grep of `src/pycsl` finds only op_translate's
  line 100 + emitter comments describing the feature). So no cheap same-recognizer follow-on — stopped.

**End count 1261 (18 handlers/leaves converted cumulatively).** byte-diff 0 held; allowlist unchanged.
The in-stack-recognizer frontier remains otherwise feature-gated (iter-21 flags stand):
`safe_exc_name` (string-valued `or` + `.lstrip(arg)`), `struct_format::arity` (`use array.Array`
preamble for a value-record array field — and note iter-21's addendum: struct_format's mirror is a
STALE stub skeleton, so arity needs the whole grown `StructFormat` shape resynced first), plus the
set-local / IR-recursion / external-callback blocked helpers. Next tractable pickup is again
smallest-feature-first (string-valued `or`, or the value-record array-preamble).

### Iteration 23 (2026-07-05) — 🎯 safe_exc_name CONVERTS via string-bool-op feature (1261→1260)

The second demand-driven feature flagged in iteration 21 (both-operands-string `or`/`and`) LANDED
(commit `16f5f6a2`): `s or t` now lowers to a faithful string ITE over emptiness
(`if str_length_op s > 0 then s else t`); `.lstrip("_")` already yields a length-bounded opaque
`string`, so `safe_exc_name(name) = name.lstrip("_") or name` lowers to a coherent string. This
iteration converts `identifiers::safe_exc_name` through the full SL loop.

- **converter:** ported the live body verbatim — `return name.lstrip("_") or name` (+ the live
  docstring). Contract shape `#@ requires True / ensures True / assigns \nothing`. NO companion type
  change needed (body touches only the `name` param, `.lstrip`, and `or` — unlike op_translate which
  needed `OP_MAP: int→Dict[str,str]`). Local `--no-proof`: L3-tc ✓.
- **Gate A:** T1.b tier, not on floor denylist, contract shape correct → APPROVED; `\trusted` removed.
- **VERIFIER (fresh, surface-only) + independent re-confirmation — three L planes, ALL PASS:**
  - **Fidelity:** `check-self-annotate-sync.sh` exit 0 ∧ `self-annotate-mirror-check.sh` exit 0
    (safe_exc_name body == live verbatim).
  - **Type-safety:** `Verification SUCCESS` — `safe_exc_name'vc` Valid via best-of-N **Z3** (sanctioned
    string-theory path). `proof_axiom_allowlist` diff **EMPTY** (no smuggled axiom).
  - **Corpus inertness:** byte-diff **0** vs the re-pinned E-0 baseline (750 corpus files identical;
    the mirror file is not in the reference sweep — mirror-only conversions are byte-diff 0 by
    construction); suite **17/27**, identical to the known pre-existing failed set
    (pycsl.py `_Directive`, expressions.py/statements.py int/string leaks, 7 unmirrored "file
    missing") — identifiers.py PASSES, no NEW failure; `\trusted` count **1261 → 1260** (canonical
    `\\trusted` marker; strict −1).
- **Gate B + Gate C:** all three planes pass, unblended; non-vacuity holds (tight `\nothing` frame,
  real verbatim body, genuine string-ITE VC discharge). No coherent-and-wrong caught. Committed
  `1b029a75`.
- **Adjacent-leaf sweep:** neither new feature (module-const-dict-get, string-or-and) cheaply unblocks
  another leaf at byte-diff 0. The only `return X or Y` in identifiers.py was safe_exc_name itself; the
  two remaining identifiers.py stubs are feature-blocked — `stable_hash` (hashlib, external opaque) and
  `whyml_ident` (per-char loop + `unicodedata.normalize`/`ord` — needs char-loop invariants + unicode
  modeling). No module-const-dict `.get(k, str_default)` consumer remains. Stopped.

**End count 1260 (19 handlers/leaves converted cumulatively; 3 this session: op_translate,
safe_exc_name, + the statements.py fidelity resync).** byte-diff 0 held; allowlist unchanged. Frontier
back to **feature-gated**: next flagged leaf is `struct_format::arity` (needs the `use array.Array`
value-record-field preamble AND a stale-`StructFormat`-stub resync — the mirror struct_format.py is a
generated stub skeleton whose live `StructFormat` has grown a `chars` field + faithful_* methods it
lacks; see iter-21 addendum). Remaining set-local / IR-recursion / external-callback helpers unchanged.

### Phase 2 (tier3-p2, 2026-07-06) — expr-ADT re-triage under FULL proof + 3 free string-leaf converts (count 1252→1249)

Executes `triage-ranked-tcb-tier3.md` T3.2.1 (re-triage the Module-6 core WITH the landed expr-ADT,
under FULL proof, not `--no-proof`) + T3.2.2 (convert the cleanly-provable set). This is the first
Phase-2 marker-payoff pass over the tier-3 ADT (commits `8993a5b9`+`d989985f`).

**T3.2.1 — re-triage (harness: splice live body verbatim → `--fun <method>` full proof → revert).**
Swept every trusted stub with a live counterpart across the Module-6 core + A6 IR-readers:
`expressions.py` (51), `statements.py` (15), `functions.py` (36, whole-file-provable), plus A6
`ir_scanner.py` (34, 18 sampled), `types.py` (18), `stmt_control_flow.py` (8 smallest). **Verdict:
CONVERTIBLE = 3; BLOCKED = all IR-node-reading handlers.** The landed ADT advances the typecheck
frontier (the tier-1 `unbound type symbol 'emit_ir'` is GONE — these node-reads now bind a type) but
NO IR-reading handler discharges a verbatim whole-body port, because each then hits one of:

- **`.get("value")` scalar-vs-subnode overload** (dominant, ~all of `expressions.py`/`types.py`). The
  recognizer maps `value`→`svalue_of : emit_ir` (a SUB-node), but literal handlers read `Number.value`
  (int) / `String.value` (str) as a *scalar leaf* → `type int, but expected string`. `_is_float_expr`,
  `_is_null_byte_lit`, `_handle_sum_call`, `_linear_form`, `_static_width`, `_val_is_bool`, … all leak
  here. This is §5e/risk-7 unresolved for the `value` leaf.
- **list-shaped `.get("elts")/.get("args")`→`args_of : array emit_ir` (OPAQUE)** — can't be iterated
  faithfully (`ArrayLit`/`SetLit`/`Tuple`/`DictLit` deferred per §9a); `_handle_sum_call`,
  `_is_null_byte_lit`, comprehension/tuple readers.
- **list-recursion TERMINATION VC** — the `IRScanner` bool scanners (`uses_arrayset`, `has_continue`,
  `uses_continue`, `uses_break`, `has_direct_return`, `ends_with_return`, `find_ghost_vars`, …)
  TYPECHECK under the ADT but the proof FAILS: recursion over a stmt/expr *list* has no `size` measure
  (`_emit_function` injects `variant {size p}` only for a scalar `emit_ir` param, not `List[ExprIR]`).
  This is exactly FRONTIER's "`--no-proof` over-counts the 19 ir_scanner leaves" — confirmed under full
  proof (0/18 sampled convert).
- **dict/map field builders** (`functions._build_method_*`, `types._collect_*`, `find_array_and_dict_vars`)
  — `Dict[str,X]` iteration → `array int`/`array string @rho` / `'mu -> option int` gaps (map-local
  modeling absent).
- **str-tag inference domain** (`types.py`) — returns type-name strings that mix with int hashes
  (`type string, but expected int`).

**T3.2.2 — CONVERTED (3, all free string/f-string LEAVES that read NO IR node — missed by the
iters-16-23 sweeps, NOT ADT-enabled):**

| file | method | shape | proof |
|---|---|---|---|
| `expressions.py` | `_array_coerce_arg` | pure `str` coercion (`@staticmethod`, `.strip`/`.startswith`/`.isalnum`) | `--fun` SUCCESS |
| `statements.py` | `_emit_new_ghost_ref` | `let ghost … in` f-string builder (calls trusted `_stmts_to_whyml` opaquely) | `--fun` SUCCESS |
| `statements.py` | `_wrap_body_with_return_catch` | return-catch wrapper, string-dispatch on return_type | `--fun` SUCCESS |

Each: verbatim live body + fixed contract (`#@ requires True / ensures True / assigns \nothing`),
`\trusted` removed. No live emitter method touched → no re-port needed (process rule N/A). Committed
`e73ec7c6`.

**Gates (streamlined §5.1, all green):** fidelity `check-self-annotate-sync` (80 un-trusted verbatim)
∧ `self-annotate-mirror-check` (51 in sync); type-safety = 3× `--fun` SUCCESS; `proof_axiom_allowlist`
diff EMPTY; corpus inertness = emitter (`src/pycsl`) git-IDENTICAL HEAD~1..HEAD (mirror-only) ⇒
byte-diff 0 by construction, belt-and-suspenders sweep emitted 756 corpus `.mlw` crash-free; **no NEW
failure** — only 2 files changed, both retain their SAME pre-existing `int`↔`string` leak verdict
(unchanged from baseline; the leak is in an unconverted method), every other suite file byte-identical
to HEAD~1. Count **1252→1249** (literal `\trusted`; full marker 1232→1229).

**Honest yield & the next Phase-1 increment (the guide for tier3-p1).** The tier-3 expr-ADT did NOT
yet yield an IR-reading marker conversion — the 3 converts are incidental free leaves. The **single
highest-leverage next Phase-1 increment is the list-shaped kinds** (`ArrayLit`/`SetLit`/`Tuple`/`args`/
`elts` as a structural `list emit_ir` + a `size_list` MUTUAL measure): it simultaneously (a) unblocks
the `.get("elts")/.get("args")` projections and (b) provides the `size` measure for **list recursion**,
which is the termination VC blocking the ENTIRE `ir_scanner` family (~34 stubs) — the largest single
cluster. Second: the **scalar-value-leaf projection** for `Number.value` (int/`ir_num`) and
`String.value` (string), splitting the overloaded `.get("value")` by receiver-kind — unblocks the
literal/affine-form readers in `expressions.py`. The stmt/contract node families and set-local/map-local
modeling remain further out. Both increments are demand-driven emitter features (spike→build→gate),
per the standing tier-2/tier-3 lesson that a marker conversion needs the value shape BUILT first.

**Phase-1 Track-R (R3 / R1' / R2) — STOP-LOSS at 1240; 0 conversions (full: `getting-better/tier3/
wall-plan-phase1.md`).** Executed the Phase-0 (`wall-plan-phase0.md`) decision "Track M HALTED,
Track-R-only" through the existing certified IR-node ADT (no new value model; `pyval`/`fmap`
untouched). Count **1240 → 1240**. Measured clean rate **0/1** direct attempt (+ the tier-5 census's
0/98 on the same surface). Findings:
- **The mirror baseline is RED at HEAD** (pre-existing, zero edits this session):
  `bin/run-self-annotation-suite.sh` FAILs on `expressions.py` (`.mlw:669`, verified
  `_handle_field_get_expr` — `_class_constants` value-type `option int` read as string) and
  `statements.py` (`.mlw:508`, verified `_handle_array_set_stmt`), both `int↔string`, plus `pycsl.py`.
  Git-traced to the WL-04f/05/06 verified-method resyncs (`4ef18975` et al.) — the SKILL §10.4 failure
  mode (re-port of a verified method that can't re-prove) landed across the WL series and degraded the
  `e73ec7c6`-era "pre-existing leak in an unconverted method" into a **whole-file typecheck failure**.
  A whole-file typecheck failure blocks `--fun` proof of EVERY method in the file (confirmed on
  `_handle_tuple_unpack_stmt`).
- **R3 BLOCKED:** its targets (`_handle_tuple_unpack_stmt` in statements.py; the `for nm,v in (…)`
  path via `_emit_metatype_tags`/`_classify_iterable`/`_handle_for_stmt`) are verified methods in RED
  files, and the `for nm,v` case is a heterogeneous-tuple-literal **value-model feature** (opaque
  `iter_length` path), not a small typing tweak — out of Track-R scope.
- **R2 = 0/1:** ADT reflection is gated on a `@mutable_state @dataclass` reader class (recognizers §7);
  the @mutable_state files are RED, the clean files (types.py/ir_scanner.py/functions.py) are plain
  classes → `.get("type")` collapses to `int` → B1. Measured `types.py::_val_is_bool` (smallest
  non-recursive incidental clean stub) → `--fun` `type string, but expected int` FAIL; reverted, 1240.
- **R1' NOT built** — unused facade = gold-plating (task's explicit prohibition) with every R2 consumer
  blocked; deferred to a green-baseline session with a co-landing consumer.
- **Actionable output:** restore the RED baseline (fix the `expressions.py`/`statements.py` verified-body
  `int↔string` leaks; audit the WL resyncs vs §10.4) BEFORE reopening Track-R Phase-1 — it blocks R3,
  ADT-routed R2, and R1' alike. Ledger held at 3 axioms; `proof_axiom_allowlist` unchanged; fidelity
  `check-self-annotate-sync` green (90 verbatim). Deliverables docs-only; no `src/pycsl`/mirror edit.

---

### Iteration — 2026-07-09 · Track A (census): V2 collection-result frontier · count held 1237

**Trigger:** SL loop re-entered at 1237 (bounded-algebra IR-fold/traversal frontier exhausted per
`bigger-build.md §7`). User chose **A — CENSUS**. Scoped to **V2 (collection-result modeling)** in the
model-addressable emitter modules (`module6_whyml/*`, `core_ir_semantic.py`) — NOT the
`frontend/pure_ast.py` (262) / `Module5_IREmitter.py` (180) flat AST-builder bulk (already out-of-frontier).

**Method:** static shape triage over the 19 collection-returning `\trusted` candidates → whole-body
`--fun` proof on the survivors (§10.1: classify on full proof, never inspection).

**Verdict — V2 yields 0 clean conversions (frontier confirmed exhausted):**
- **16 / 19 out-of-frontier by static shape:** the `functions.py::_build_method_*_map` family (10) returns
  `Dict[str, List[Dict[str,Any]]]` — **nested-pyval dict-values** (ensures-clause AST subtrees), V1-adjacent,
  not the flat `sdict` frontier; the `Set[str]`/`List` collectors (`_typed_local_vars`, `find_iteration_mutations`,
  `_build_method_param_types_map`) **compose non-algebra `\trusted` siblings + write self-state**
  (`self._ghost_tuple_vars.update`, `self._inline_array_temps = …`) — the D-outlining-over-non-algebra class.
- **3 static survivors, all fall under full proof:**
  - `types.py::_split_tuple_type` — **PROOF FAILED, measured:** ported live body
    (`rt.strip(); inner[1:-1]; inner.split(",")` comprehension) → `This expression has type int, but is
    expected to have type array string`. The `str.split(sep) -> List[str]` (whole-list, not element-index)
    chain leaks `int`; the faithful-`split`-into-`array string` op is **not modelled**. Reverted, 1237.
  - `scc.py::compute_sccs` — nested recursive **closure** (`strongconnect`) over captured mutable state +
    **non-structural recursion** (variant = unvisited-node count). Out-of-frontier.
  - `scc.py::sort_functions_by_scc` — composes `compute_sccs`. Out.

**One bounded feature surfaced (Track-B candidate, NOT research-grade):** faithful
`str.split(sep) -> array string` (extends the landed faithful-string-op P1–P4 which did split-**elem** but
not whole-list split). Would unblock `_split_tuple_type` (+1) and any sibling whole-list-split string method.
A bounded emitter feature, gated like any Track-B build (both provers, byte-diff 0, whole-body proof).

**Outcome:** census confirms the residual V2 frontier is at the honest floor — the tractable slice is
`str.split` alone. No conversion landed (correct — measure before build); tree clean, count 1237, ledger==3.

---

### Iteration — 2026-07-09 · Track B (build): faithful whole-list `str.split` → `array string` · 1237 → 1236

**Trigger:** the V2 census (above) surfaced ONE bounded feature — the whole-list
`str.split(sep) -> array string` op (the landed faithful-string-op P1–P4 did split-**elem**
`s.split(sep)[i]` but not the whole list). User chose **B — BUILD**. Gated per §3/§5.1/§10.

**Built (emitter, `src/pycsl/module6_whyml/`):**
- `expressions.py::_split_comp_array_string` — recognizes a comprehension
  `[<str-elt> for t in <string>.split(sep)]` (single generator, split source, element
  string-typed once the loop target is bound to `str`) → an OPAQUE `array string`
  (`val str_split_op (s sep: string) : array string ensures { Array.length result >= 0 }`).
  A sound under-approximation (content unmodelled, like `str_split_elem_op`); the per-element
  transform is dropped, sound under the `ensures True` self-annotation contract. Placed AFTER
  the `@mutable_state` block (which already lowers a string comp to `list_comp_string`), so it
  fires only for non-mutable-state files — the two never disagree.
- `ir_scanner.py::uses_str_split_comp` + `preamble.py` `needs_array` wiring — a `ListComp` over
  a `.split`/`.rsplit` iterator now triggers `use array.Array` (else `str_split_op : array string`
  hits `unbound type symbol 'array'` in a file with no other array). Loose scanner (no dataflow):
  it also fires on a non-string-receiver split-comp (`pycsl.py::args.provers.split(",,")`), whose
  recognizer does NOT fire — a harmless unused `use array.Array` import; the file still proves.

**Converted:** `types.py::_split_tuple_type` (`rt.strip(); inner[1:-1]; [p.strip() for p in
inner.split(",")]`) — the census's measured blocker — now full-file-proves. `\trusted` 1237 → 1236.

**Gates (all green):** type-safety — mirror `types.py` full-file `Verification SUCCESS`; fidelity
— `self-annotate-mirror-check` 52/52 in sync; corpus inertness — **byte-diff 0** over 759 corpus
files (reliable in-tree baseline; the worktree baseline was invalid — no `.venv`) with all 3 emitter
files changed; ledger — **==3**, `src/formal-semantics` + `proof_axiom_allowlist` untouched, NO new
axiom (`str_split_op` is a `val` with a sound length law), NO new value shape (`array string`
pre-existing → no certificate); suite — the changed-emission mirrors (`types`/`pycsl`/`preamble`) all
re-proved, unchanged-emission mirrors byte-identical to HEAD (no other split-comp in the mirror tree).
Reference fixture **0885** (positive) proves under the feature emitter.

**Outcome:** +1 marker (1236), a reusable faithful whole-list `str.split` lowering banked. The next
whole-list-split string method in the mirror is now convertible on the same op.
