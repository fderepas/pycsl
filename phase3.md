# phase3.md — the collection-result families (A-set / A-list / A-dict)

**Status: PLAN of record for bigger-build Phase 3. Execution starts after this file lands.**
**Parent: `bigger-build.md` (§1 families, §3 protocol, §5 gates, §7 ledger). Reuses the landed
`GenericFold` infra (`src/pycsl/module6_whyml/generic_fold.py`), the certified L1 `pyval`/`pydict`/`size`
theory + Rocq/Lean certificate, and the `doc` model.**

---

## 0. Context and the VERIFIED reality this plan must respect

Banked & verified: the wall is broken in practice — `find_named_expr_targets` (A-unit) converts via a
certified catamorphic lowering (count 1247, no new trust/axiom, byte-diff 0). But two scaling attempts
**deferred on contact with real bodies** (Phase 1b check-walks; Phase 2 A-doc `find_return_type`), proving
the decisive lesson:

> **The v3 census classified by the OUTER walk shape; real complexity lives in the pre-action /
> composition / control-flow.** The family counts (≈259 "collection-result builders") are **UPPER
> BOUNDS**. Real methods compose sibling-helper walks, do short-circuit / early-return search, use
> variable-key context lookups, and thread value-dependent control flow — none of which the pure
> catamorphic template captures. **Same over-count as tier-1/tier-5.**

So Phase 3 is **census-refinement-first and measure-before-build**: we do NOT assume the 259 convert. We
split them by result type AND re-verify each against its live body to find the **CLEAN self-contained
fold** subset per family — expecting it to be materially smaller than 259.

## 1. The families and what is genuinely NEW per family

The `GenericFold` recognizer/templater and the `pyval`/`pydict` walk skeleton are reused. The **new part
per family is the RESULT ALGEBRA** — a faithful WhyML model of the *returned collection*, co-landed with
an **axiom-free Rocq 8.20 + Lean 4.29 certificate** (the coupling rule; ledger stays 3). This is the
tier-5 "V2" collection-result gap, now attacked with the certified-value discipline.

| family | source shape | result-algebra value model needed | reuse |
|---|---|---|---|
| **A-set** | `out=set(); … out |= self(v)/out.add(k); return out` | a faithful returned-`set string` (candidate: `Fset string`, or `map string bool` à la L1's `set_add`) + a fold-into-set lemma pack | L1 `set_add`/`pystr_eq` already model the *ref* case — the returned case is the by-return twin |
| **A-list** | `out=[]; … out += self(v); return out` | a faithful returned-`list τ` (element type from the accumulation) + append/concat fold lemmas | L1 `list` + `size_list` |
| **A-dict** | `out={}; … out.update(self(v)); return out` | a faithful returned-`pydict`/`map` result + merge/update fold lemmas | L1 `pydict` (the value model already exists) |

A-set is likely the most tractable (its ref-twin already converted); A-dict reuses `pydict`; A-list needs
element-type inference. Each is its own **go/no-go**.

## 2. Phase 3.0 — census refinement (THE go/no-go; measurement only, no code)

Take the ≈259 "collection-result / out-of-pattern-builder" rows from the v3 census
(`getting-better/tier3/wall-plan-v3-phase0.md` + `scratchpad/census_final_v3.json`). For EACH:
1. **Split by result type** → A-set / A-list / A-dict / A-bool (predicate) / other.
2. **Re-verify against the LIVE body** (not the structural shape): is it a **CLEAN self-contained fold**
   (single self-recursive walk; accumulate into the returned collection via `|=`/`+=`/`.update`;
   literal-key reads; NO sibling-helper call, NO composed second fold, NO short-circuit/early-return
   search, NO variable-key context lookup)? Or **complicated** (any of those)?
3. Record per method: family, clean|complicated, the deciding body feature.

**GATE / deliverable:** the **clean count per family**. If clean ≈ 0 across families (i.e., the
collection-builders are as composed/dependent as the check-walks were), Phase 3 is a NO-GO and we bank —
same honest boundary as before. If a family has a worthwhile clean subset (say ≥5), that family proceeds.
This step alone decides whether Phase 3 is worth the per-family model builds. **Deliverable:**
`getting-better/tier3/phase3-census-refinement.md` + the clean-subset lists.

## 3. Per-family build protocol (only for families with a clean subset; each gated)

For each GO family, in tractability order:
1. **Spike the target shape** (hand-write + prove on Alt-Ergo AND Z3, no axiom, false twin unproven): the
   `walk`/`walk_dict`/`walk_list` group returning the collection, built by the fold-into-collection algebra
   + its termination (`size`-variant) + the result-model lemmas. A NO-GO here ⇒ the family stays
   `TRUSTED(essential)`, ledgered; do not force.
2. **Co-land the result-model certificate** — axiom-free Rocq + Lean for the returned-collection value +
   its fold lemmas; assert ledger==3 (`Print Assumptions` / `#print axioms`). A 4th axiom ⇒ HALT the family.
3. **Extend the templater** to the result algebra (by-return slot instead of the ref accumulator) + extend
   the recognizer (fail-closed; near-miss fixtures must still not fire).
4. **Convert** the clean subset: port verbatim, `\trusted` removed, per-instance **FULL-FILE proof**,
   byte-diff 0 (+ poisoned control once), feature-touches-verified-method re-port.
5. **Gate + per-family stop-loss** (two batches <50% clean → stop the family, ledger the rest).

## 4. Phase order
- **3.0** census refinement (go/no-go, above).
- **3.1** A-set (ref-twin already proven → most tractable).
- **3.2** A-dict (reuses `pydict`).
- **3.3** A-list (needs element-type inference).
- Then bigger-build Phase 4 (LINK-2 `cata` tag note + scale-out + stop-loss).

## 5. Disciplines / gates (carry over — non-negotiable)
Ledger==3 (`Print Assumptions`/`#print axioms` after any certificate); byte-diff 0 (gated recognizer +
poisoned control); per-instance re-proof = no new trust; measure-before-build (spike each family first);
full-file proof in the gate (not `--fun` — the masking lesson); feature-touches-verified-method re-port;
single-writer; independent review of the recognizer spec + template text; **I re-verify every agent claim
myself** (re-prove full-file, re-run byte-diff/suite/ledger).

## 6. Honest expectations
The census over-count warning applies **most** here. Realistic outcome: a small clean subset per family
(the self-contained builders like `find_ghost_vars`), a real `+N` where each family's model lands, and a
majority staying `TRUSTED(essential)` (the composed/sibling/short-circuit builders). The **prize is the
capability** — a certified returned-collection fold coupled to `pyval` — not the raw 259. Measured, not
projected; per-family go/no-go; bank honestly at the clean floor.

## 7. Execution ledger
- [ ] 3.0 — census refinement (clean-count per family; go/no-go)
- [ ] 3.1 — A-set (spike → certificate → template → convert clean subset)
- [ ] 3.2 — A-dict
- [ ] 3.3 — A-list
