# triage-ranked-tcb-tier3.md — TIER-3 sub-plan: the IR-node value ADT (+ formal-semantics Phase 7)

Detailed execution plan for TIER 3 of `triage-ranked-tcb.md` — the recursive typed value ADT that
gates ~90% of the `\trusted` frontier AND (as tier-2a proved) the tier-2 marker conversions too.
This is a research-grade, multi-week effort, **not** a squeeze-loop pass.

> ## ✅ STATUS: EXECUTED — CLOSED AT PATH 1 (2026-07-06)
> Tier 3 passed its Phase-0 STOP gate (GO) and built the certified foundation; the corrected v2 track
> (`attic/triage-ranked-tcb-tier3-phase3-v2.md`) then MEASURED the real payoff and CLOSED the marker
> campaign. `\trusted` count **1249 → 1240**. Outcome vs. the ambition in the sections below:
> - **Phase 0 ✅** (GO, no new axiom) · **Phase 3 ✅** (conservative certificate, 3-axiom ledger held;
>   deep `VRec` integration deferred, not needed) · **Phase 4 ✅** (both leave-trusted).
> - **Phase 1 ◑** — the **expr family landed (9 kinds)**; the **stmt / contract / list-shaped families were
>   deliberately NOT built**.
> - **Phase 2 ◑** — **9** `ir_scanner` walkers converted, **NOT** the "~150–200" projected in §Phase 2 below.
> - **Why closed:** the whole-body census (`getting-better/tier3/whole-body-census.md`, commit `7a750917`)
>   measured the ADT's ENTIRE reachable payoff at **≤ 19 of 164 stubs**, with **86% (141) a semantic ceiling
>   the ADT cannot reach** (raw `Dict[str,Any]` typing, collection modeling — blocked *upstream* of any IR
>   node kind). An independent adversarial review (`getting-better/tier3/plan-review.md`) verified the
>   certified foundation reproduces but refuted the large-payoff projection.
> - **Residual** (`getting-better/tier3/step-d-leave-trusted-analysis.md`): 2 LEAVE-TRUSTED (WL-05,
>   conversion impossible + valueless) + 141 TRUSTED-PENDING (separate value-model gaps, low-ROI,
>   demand-driven) + 4 irreducible floor.
>
> **The "~90% of the frontier" / "~150–200 payoff" framing in the sections below is the PRE-EXECUTION
> AMBITION — it was REFUTED by measurement.** The durable deliverable is the **certified ADT foundation**,
> not a large marker cut. The per-phase plan below is kept for the record; read it through this banner.

## 0. Objective, coupling principle, and the STOP gate

**Objective.** Give the emitter's heterogeneous IR nodes (the `{"type": K, ...}` dicts that Module 6
consumes) a faithful WhyML value type — a **variant/record ADT** — so that emitter code doing
`ir.get("type")` (discriminant), `ir.get("field")` (typed sub-node/leaf projection),
`isinstance`/`type()` dispatch (`match`), and structural recursion over sub-nodes can **self-verify**.
This is the exact construct that failed to lower in tier-1 (`emit_ir` unbound) and tier-2a
(`_rr.get("name")` IR-reflection).

**Coupling principle (INVIOLABLE — from LINK 1/2/3, `src/formal-semantics/README.md §8.1a`).** The
IR node is a *nested record/variant* (a `BinOp` holds `left`/`right` sub-nodes). Modeling
`ir.get("right")` needs a **record-valued `val` with nested projection** — precisely the deferred
**Phase 7** item ("record-valued `val` for nested aliasing", README §2.2). Building the emitter-side
ADT WITHOUT the Phase-7 certificate would let the self-annotation verify against a WhyML construct the
mechanized soundness proof does not yet cover — capability outrunning its certificate. **Therefore the
emitter ADT (Phase 1 here) and the formal-semantics Phase-7 model (Phase 3 here) must land as a
matched pair; neither merges without the other.**

**STOP gate (Phase 0 decides go/no-go).** If either the WhyML ADT (P0.2) or the Rocq/Lean Phase-7
model (P0.3) is shown infeasible/unsound, TIER 3 is **not tractable yet** → document, leave the mass
trusted, and stop. Do not partially build (a half ADT that only type-checks is the tier-2a trap).

**Value-first scoping.** Target the **Module-6 emitter core** ADT (the IR-dict node model) — highest
soundness value (it's what LINK 1/2/3 certifies) and it unblocks tier-2. Treat `pure_ast`'s Python-AST
ADT (~258) and `proof2why3`'s `Term` ADT (~130) as **prioritize-by-value = LEAVE TRUSTED** (Phase 4),
converting only if a specific soundness need arises.

---

## Phase 0 — Feasibility & scope pinning (spikes only; NO src commitment) — ✅ DONE (GO)

**T3.0.1 — Enumerate the IR-node surface (the ADT signature).**
- Read `src/pycsl/ir_schema.py` (ExprIR / stmt / contract node kinds + fields) and how
  `module6_whyml/expressions.py::_expr_to_whyml` + `statements.py`/`stmt_control_flow.py` dispatch on
  `ir["type"]`. Produce a CLOSED enumeration: every node kind `K`, its fields, and each field's type
  (leaf: int/str/bool; sub-node: recursive; list-of-sub-node).
- Cross-check against the formal-semantics inductives (`rocq/Phase1_AST.v` `expr`/`contract_expr`/
  `stmt`; `lean/.../AST.lean`) — the SUBJECT-language model already enumerates these; the emitter ADT
  is the emitter's-eye-view of the same shapes.
- **Deliverable:** `getting-better/tier3/ir-node-adt-signature.md` — the variant signature (this is the
  spec both P1 and P3 build to). **Gate:** the enumeration is closed (no open `Any`/`**kwargs` node).

**T3.0.2 — WhyML ADT feasibility spike (make-or-break, emitter side).**
- Hand-write `test-suite/corpus/conformance/spikes/tier3_ir_node_adt_spike.mlw`: a variant
  `type ir_node = Var str | BinOp op ir_node ir_node | Subscript ir_node ir_node | Call str (list ir_node) | ...`
  for a REPRESENTATIVE expr subset. Prove: (a) discriminant/`match` dispatch, (b) sub-node projection
  (`match n with BinOp _ l _ -> l`), (c) STRUCTURAL RECURSION with a termination measure
  (subtree-size `variant`), (d) a field-read law, all on **Alt-Ergo AND Z3**, NO new axiom.
- Confirm the Why3 constraints: variant must be PURE (no mutable field inside — the `array (array τ)`
  rejection class); a list-of-sub-nodes field uses `list`/`seq`, not `array`.
- **Deliverable:** the spike + a verdict note. **STOP if it can't discharge without an axiom.**

**T3.0.3 — formal-semantics Phase-7 feasibility spike (certificate side).**
- Rocq: extend `Phase2_State.v` with a record-VALUED `val` (nested record in the state), add a
  read-back lemma (`o.b.c := v ⟹ o.b.c = v`), confirm it composes with `eval_expr`/`wp`. Prove a
  minimal soundness fragment. Mirror in Lean (`State.lean`).
- **Deliverable:** `src/formal-semantics/{rocq,lean}` spike files + a verdict. **STOP if the
  record-valued `val` breaks `pycsl_soundness` or needs a new axiom** (the ledger must stay at 3 axioms).

**T3.0.4 — COUPLING check (LINK-2/3).**
- Confirm the emitter's ADT (T3.0.2) emits WhyML whose semantics the Phase-7 model (T3.0.3) certifies:
  the `emit_stmts_coherent` / `module6_encodes_mlw` discipline extended to the ADT node reads. A small
  byte-diff cross-check (the LINK-2 26/26 style) on one representative handler.
- **Deliverable:** a coupling note. **Gate: go/no-go for Phase 1–3.** Present this decision to the
  human before any src edit.

---

## Phase 1 — The IR-node ADT in the Module-6 emitter (build, gated per node-family) — ◑ EXPR ONLY

> **Status: expr family DONE (9 kinds, commits `8993a5b9`+`d989985f`); stmt/contract/list families NOT
> built — closed at PATH 1 (see top banner).** The census showed no further family clears v2 §5's calculus.

Only on a Phase-0 GO. Build incrementally by node-family; each family is a full gated feature.

**T3.1.1 — Emit the `ir_node` variant type in the WhyML preamble.**
- `module6_whyml/preamble.py`: emit the pure variant `type ir_node = ...` (from T3.0.1 signature),
  gated on an IRScanner flag so programs with no IR-node param are byte-identical.
- **Gate:** byte-diff 0 on the reference corpus (additive); the type Why3-typechecks.

**T3.1.2 — Model `ir["type"]` discriminant + `ir[field]` projection (expr nodes first).**
- `module6_whyml/expressions.py` (+ `types.py`): recognize a param/local typed `ExprIR` (or the wire
  `emit_ir`) as `ir_node`; lower `ir.get("type") == "K"` to a `match`/discriminant test and
  `ir.get(field)` to the constructor projection. Fail-closed for an unrecognized node kind.
- **Gate:** spike + POS/false-twin drivers + reference locks (POS: a handler reads
  `BinOp.op`/`.left`/`.right` faithfully; NEG: wrong-field projection stays UNPROVEN) + byte-diff 0 +
  docs (translational + static-semantics + `ir-node-adt-signature.md`). Alt-Ergo+Z3, no axiom.

**T3.1.3 — Model `isinstance`/`type()` dispatch as `match`.** Same gate.

**T3.1.4 — Model structural recursion over sub-nodes (termination `variant`).**
- The `_expr_to_whyml`/`_stmts_to_whyml` dispatchers recurse into sub-nodes. Emit a function-level
  `\variant` on the subtree measure (node size/depth) so termination discharges. This is the piece
  tier-1's `ir_scanner` needed and lacked.
- **Gate:** a recursive handler proves (terminates) full-proof, not just `--no-proof`.

**T3.1.5 — Repeat T3.1.2–3.1.4 for the stmt node family and the contract-node family.**
- One gated increment per family. Reuse the variant + recursion machinery.

---

## Phase 2 — Convert the Module-6 emitter-core cluster (the marker payoff) — ◑ 9 CONVERTED, CLOSED

> **Status: 9 `ir_scanner` walkers converted (count 1249→1240, commit `7e398d4e`); campaign CLOSED at
> PATH 1.** T3.2.1's re-triage was done AS a whole-body census (`whole-body-census.md`) and REFUTED the
> "~150–200" projection: the ADT's whole reachable set is ≤19, 86% is an unreachable semantic ceiling.

Only after the relevant Phase-1 family lands.

**T3.2.1 — Re-triage the Module-6 core under FULL proof** (not `--no-proof`). Re-run the A5/A6 stubs
(`expressions.py` 53, `statements.py` 43, `functions.py` 36, helpers) against the now-available ADT;
produce the actually-convertible list (per the tier-1 lesson).

**T3.2.2 — SL-convert the freed cluster, streamlined gate (SKILL §5.1), per file, per-function proof
where recursive.** Each converted handler: verbatim live body + fixed contract, prove the changed
file, fidelity green, count strictly down. **Obey the process rule:** any handler whose live body was
touched by a Phase-1 recognizer change must be re-ported + re-proved in that same commit.

**T3.2.3 — Interleave the certificate:** for each converted handler class, add/confirm the
Phase-7-backed WhyML-correctness lemma (Phase 3) so the conversion's soundness is anchored, not just
type-checked. (This is the LINK-3 `*_code_state_coherent` discipline extended to ADT node reads.)

**Expected yield:** ~~the ~150–200 Module-6-core stubs — the real TCB reduction~~ — **REFUTED by the
whole-body census: actual reachable yield ≤ 19 of 164; realized 9.** (The projection assumed "node
kind" was the blocker; the real blocker is *reflection style* — generic `Dict[str,Any]` walks + the
86% semantic ceiling are outside the ADT's reach.)

---

## Phase 3 — formal-semantics Phase 7 (the certificate; co-lands with Phase 1/2) — ✅ DONE (conservative)

> **Status: DONE conservatively (commit `959f30c3`).** The record-valued `val` is a compiled side-car
> (`Phase2b_RecordVal.v`, `RecordVal.lean`) — read-back/frame/conservativity proved, `pycsl_soundness`/
> `pycslSoundnessVerified` re-prove UNCHANGED, `Print Assumptions`/`#print axioms` identical to baseline
> (3-axiom ledger held), independently reproduced. The DEEP integration below (T3.3.1's `VRec` into core
> `val` + the SOS/WP/Phase6 cascade) was **deliberately NOT done** — it isn't needed for what Phase 1
> emitted, and doing it is what would have risked the ledger. Reinstate only if a future step needs a
> value shape the side-car can't cover.

**T3.3.1 — Rocq: record/ADT-valued state.** Extend `Phase2_State.v` (`val`, `state`, `lookup`,
`update`, `eval_expr`) with nested record values; extend the SOS (`Phase3_SOS.v`), the WP arms
(`Phase4_WP.v`), and the Module-6 encoding (`Phase6d_StmtGen.v`, `Phase6m_VcgSemBridge.v`) for
ADT-node reads/projections. Re-prove `pycsl_soundness` (`Phase5b_Soundness.v`) — **0 new Admitted,
trust ledger stays at 3 axioms**.

**T3.3.2 — Lean: mirror T3.3.1** (`State.lean`, `SOS.lean`, `WP.lean`, `StmtGen.lean`,
`Soundness.lean`) — 0 `sorry`, `pycslSoundnessVerified` re-proves.

**T3.3.3 — Update `src/self-annotate/pycsl-wp-spec.mlw` (LINK 3)** with the per-arm coherence lemma for
the ADT node reads; keep the D2 evaluator-axiom boundary enumerated + audited
(`evaluator-axiom-audit.md`). Re-run the LINK-2 byte-diff cross-check.

**T3.3.4 — Update `src/formal-semantics/README.md`:** move the record-valued-`val` item from §2.2
"deferred" to done; refresh the status table and the 3-axiom ledger note.

---

## Phase 4 — Peripheral subsystems (DECISION: leave trusted, by value) — ✅ DONE

**Full analysis + evidence: `getting-better/tier3/phase4-peripheral-decision.md`.** Both
leave-trusted, with the residual gap named precisely per subsystem (not hand-waved "peripheral").

**T3.4.1 — pure_ast (~258) — Python-AST ADT. DECISION: LEAVE TRUSTED.** *False-verifies verdict:*
**POSSIBLE in principle** — `pure_ast` is UPSTREAM of the certified resolved-IR boundary
(`docs/ir.md §1`; README §9 "Python parser = TRUSTED BY DESIGN"), so a silent structural misparse
makes PyCSL verify a program other than the source. This is a **genuine, distinct trust boundary
(source→IR faithfulness), NOT the WP-soundness the 3-axiom ledger covers** — stated honestly, not
glossed. *Why leave-trusted anyway:* **conversion would NOT close the gap** — self-annotation proves
each method's own type-safety/frame, never "the tree faithfully represents Python's grammar" (there
is no mechanized Python grammar to verify a self-contract against). The gap is instead **compensated**
by (a) fail-closed `PyCSLSyntaxError` (never a wrong tree), (b) the CPython differential oracle
(512/517 byte-identical `ast.dump`, 0 mismatch, per the module COVERAGE MANIFEST), (c) the standing
`bin/frontend-only-conformance.py` source→IR check. Cost is the frontier's **largest** ADT (full
CPython `ast.*` hierarchy + dynamic getattr/setattr + tokenize/RDP state). *Flip condition:* only if
a verified grammar-faithfulness artifact is wanted AND a mechanized Python grammar exists — even then,
strengthen/CI-wire the differential oracle, don't convert.

**T3.4.2 — proof2why3 (~115–130) — `Term` variant ADT + s-expr/JSON tree. DECISION: LEAVE TRUSTED.**
*False-verifies verdict:* **IMPOSSIBLE — fail-stop / assurance-degradation only.** Decisive code fact:
`proof2why3` is **NOT on the runtime trust path** — `pycsl.py` never imports it; the verifier trusts
the **hand-curated `_AXIOM_REGISTRY`** in `preamble.py`, and each cited axiom is independently
anchored by the dual Rocq/Lean proof + `--audit-proof --reverify` (kernel-axiom allow-list).
`proof2why3` is an *offline* 3-way cross-check + candidate-emit tool; a bug can only degrade an
assurance check or fail-stop, never inject an axiom. *Flip condition:* only if `proof2why3 emit` is
ever wired to auto-populate `_AXIOM_REGISTRY` **without** the human-review + `--audit-proof --reverify`
gate — then it moves onto the trust path.

**T3.4.3 — Updated `triage-ranked-tcb.md` §Tier 3 + `FRONTIER-TRIAGE.md` Phase-4 rows** with the
final leave-trusted outcome and the sharpened per-subsystem soundness classification. ✅

---

## Gating discipline (applies to every T3.1/T3.2 increment)
- **Streamlined per-stub gate** (SKILL §5.1): prove changed file only, mirror-only git-diff assertion,
  batch the suite/sweep.
- **Spike-first, both provers, no new axiom** — every emitter feature (Phase 1) and every Phase-7
  extension (Phase 3).
- **Feature-touches-verified-method rule:** re-port + re-prove the mirror method in the same commit.
- **Single-writer** on the working tree; **full-proof (`--fun`) classification**, never `--no-proof`.
- **byte-diff 0** on the reference corpus for every Phase-1 emitter change (additive).

## Risk register
| risk | mitigation |
|---|---|
| WhyML variant can't express the IR shape soundly | T3.0.2 STOP gate before any build |
| Phase-7 record-valued `val` breaks soundness / needs a 4th axiom | T3.0.3 STOP gate; ledger must stay at 3 |
| Emitter ADT outruns the certificate | Coupling rule: Phase 1 and Phase 3 co-land; T3.0.4 check |
| Recursion termination VCs churn (tier-1 lesson) | T3.1.4 structural `\variant` + per-function proof |
| Surface not closed (`Any`/dynamic nodes) | T3.0.1 closed-enumeration gate; fail-closed on open kinds |
| Effort sink on peripheral markers | Phase 4 = leave `pure_ast`/`proof2why3` trusted (value-first) |

## Exit criteria (tier-3 "done") — met under PATH 1 (re-scoped by the census)
- ◑ The Module-6-core **expr** ADT is landed (Phase 1) and its convertible cluster verified (Phase 2):
  count reduced to the **PATH-1 floor 1240**. NOTE: "the Module-6-core floor" as originally imagined
  (all families converted) is **not achievable via the ADT** — the census proved 86% is an unreachable
  semantic ceiling, so the honest floor is 1240 + the documented residual, not a full conversion.
- ✅ `pycsl_soundness` / `pycslSoundnessVerified` re-prove with the (conservative) Phase-7 model,
  **3 axioms, 0 Admitted/sorry**; independently reproduced. LINK-3 unchanged; `evaluator-axiom-audit.md`
  current (§3b).
- ✅ `pure_ast`/`proof2why3` decisions documented (both leave-trusted) + the residual split
  (`step-d-leave-trusted-analysis.md`).
- ✅ All gates green (fidelity 90/90, mirror-check 51/51, conformance 38/38, corpus byte-diff 0,
  doc-coherency); no new axiom.

**Verdict: tier-3 is CLOSED.** Foundation certified + banked; marker payoff harvested (9); the rest is
a semantic ceiling the ADT cannot reach (leave-trusted / trusted-pending). See the top banner.

## Dependency order (critical path)
`T3.0.1 → T3.0.2 ∥ T3.0.3 → T3.0.4 (GO/NO-GO)` →
`T3.1.1 → T3.1.2 → {T3.1.3, T3.1.4} → T3.1.5` (co-landing `T3.3.1 ∥ T3.3.2`) →
`T3.2.1 → T3.2.2 ∥ T3.2.3 (with T3.3.3)` → `T3.3.4` → `T3.4.*`.
Phase 0 is cheap and reversible; the GO/NO-GO at T3.0.4 is the one decision that authorizes the
expensive Phases 1–3.
