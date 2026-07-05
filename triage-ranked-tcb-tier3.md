# triage-ranked-tcb-tier3.md — TIER-3 sub-plan: the IR-node value ADT (+ formal-semantics Phase 7)

Detailed execution plan for TIER 3 of `triage-ranked-tcb.md` — the recursive typed value ADT that
gates ~90% of the `\trusted` frontier AND (as tier-2a proved) the tier-2 marker conversions too.
This is a research-grade, multi-week effort, **not** a squeeze-loop pass.

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

## Phase 0 — Feasibility & scope pinning (spikes only; NO src commitment)

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

## Phase 1 — The IR-node ADT in the Module-6 emitter (build, gated per node-family)

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

## Phase 2 — Convert the Module-6 emitter-core cluster (the marker payoff)

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

**Expected yield:** the ~150–200 Module-6-core stubs — the real TCB reduction. Track the running count.

---

## Phase 3 — formal-semantics Phase 7 (the certificate; co-lands with Phase 1/2)

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

## Phase 4 — Peripheral subsystems (DECISION: leave trusted, by value)

**T3.4.1 — pure_ast (~258) — Python-AST ADT.** RECOMMEND leave trusted: peripheral to the WP-soundness
LINK 1/2/3 story (the AST reader is upstream of the certified emitter). Document the decision; convert
only if a specific soundness gap demands it. (If ever done: a second ADT for CPython `ast.*` nodes,
same shape as Phase 1 but a distinct, larger surface + dynamic getattr/setattr/tokenize dependence.)

**T3.4.2 — proof2why3 (~130) — `Term` variant ADT + s-expr/JSON tree.** RECOMMEND leave trusted:
peripheral (the Rocq/Lean s-expr parser is the cited-proof *ingestion* path, not the WP core); also
subprocess/regex-gated. Document.

**T3.4.3 — Update `triage-ranked-tcb.md` + `FRONTIER-TRIAGE.md`** with the final tier-3 outcome +
whichever peripheral decisions were taken.

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

## Exit criteria (tier-3 "done")
- The Module-6-core ADT is landed (Phase 1) and its convertible cluster is verified (Phase 2), with
  the count reduced to the Module-6-core floor.
- `pycsl_soundness` / `pycslSoundnessVerified` re-prove with the Phase-7 model, **3 axioms, 0
  Admitted/sorry** (Phase 3); LINK-2 byte-diff green; `evaluator-axiom-audit.md` current.
- `pure_ast`/`proof2why3` decisions documented (leave-trusted unless converted).
- All gates green (fidelity, mirror-check, doc-coherency, corpus byte-diff 0); no new axiom.

## Dependency order (critical path)
`T3.0.1 → T3.0.2 ∥ T3.0.3 → T3.0.4 (GO/NO-GO)` →
`T3.1.1 → T3.1.2 → {T3.1.3, T3.1.4} → T3.1.5` (co-landing `T3.3.1 ∥ T3.3.2`) →
`T3.2.1 → T3.2.2 ∥ T3.2.3 (with T3.3.3)` → `T3.3.4` → `T3.4.*`.
Phase 0 is cheap and reversible; the GO/NO-GO at T3.0.4 is the one decision that authorizes the
expensive Phases 1–3.
