# `field_to_str_frame`: Z3 cannot APPLY the nested-∀ frame axiom; Alt-Ergo can — pin the citation site

DATE: 2026-06-18
LOOP: test-supervise-sl (rung-1 `field_to_str_frame` landing)
STATUS: CONFIRMED (measured, both provers, isolated probe)
KIND: ergonomic / prover-divergence finding (affects the FUTURE `_write_dir_entry` citation)
RESOLUTION: IMPLEMENTED 2026-06-18 — per-goal best-of-N prover dispatch landed in
`src/pycsl/pycsl.py` (`_dispatch_provers`/`_merge_best_of_n`/`_verdict_rank`). The
"Proposed ergonomic fix" below is now the shipping behaviour: each `-P` prover runs
as its own `why3 prove` call and a goal is Valid iff ANY prover returns Valid
(early-exit once all goals are Valid; single `-p <prover>` keeps the byte-identical
legacy single-call path). `0714.py` now verifies SUCCESS under the DEFAULT pipeline
with NO `# pycsl-flags: -p alt-ergo` pin (removed). Corpus emission byte-diff: 0/605
(proving change only). The future `_write_dir_entry` citation site no longer needs an
Alt-Ergo pin — the default pipeline picks up the Alt-Ergo win automatically.

## What landed (rung-1, this run)
`field_to_str_frame` — the disjoint-region byte-locality frame for the `field_to_str`
codec — is now a permanent, emission-gated, UNCITED registry axiom
(`_AXIOM_REGISTRY` in `src/pycsl/module6_whyml/preamble.py`), cross-validated
zero-TCB in BOTH provers and exhibited at `0714.py` +
`0714.proofs/{rocq,lean}/FieldToStrFrame.{v,lean}`. Corpus byte-diff: 0 diffs on
the shared corpus (inert).

## The finding (the thing to surface)
Applying the axiom requires discharging its NESTED UNIVERSAL antecedent

    ( forall i. 0 <= i < width -> d0[off+i] = d1[off+i] )  ->  field_to_str d0 ... = field_to_str d1 ...

from the caller's MATCHING `forall i` hypothesis. Measured on the EXACT emitted VC
(`why3 prove -a split_vc`, --timelimit 30):

| prover            | result   | steps  |
|-------------------|----------|--------|
| Alt-Ergo 2.6.2    | **Valid**| 20     |
| Z3 4.13.3         | Unknown  | 17627  |

Z3 does NOT fire / does NOT discharge the inner-∀ antecedent here, regardless of:
- explicit two-decode trigger `[field_to_str d1 ..., field_to_str d0 ...]`,
- single-decode trigger, byte-term trigger, or NO trigger (Why3-selected),
- chained `0 <= i < width` vs `(0<=i) && (i<width)`,
- concrete width (30) vs abstract width.

This is NOT present for the single-conclusion round-trip (`field_to_str d off w = name`,
0708) — Z3 applies THAT fine (its conclusion binds a concrete `name`, no
∀-from-∀ step). The frame's conclusion is decode = decode, so the caller must prove
the universal antecedent, which is where Z3 and Alt-Ergo diverge.

## Why it matters for the retirement (the load-bearing consequence)
PyCSL invokes `why3 prove -P Alt-Ergo -P Z3` as a SINGLE call. Why3's multi-`-P`
semantics report the LAST `-P` (Z3) per goal — it is NOT an "Alt-Ergo-then-Z3
fallback". So a goal that ONLY Alt-Ergo proves is reported as Z3 Unknown and the
file FAILS the default pipeline. The 0714 exhibit therefore carries
`# pycsl-flags: -p alt-ergo` (a first-class pipeline prover that APPLIES the axiom).

The future `_write_dir_entry` / `_zero_entry` retirement that CITES this axiom will
hit the same wall: any method whose VC needs `field_to_str_frame` will need either
(a) `# pycsl-flags: -p alt-ergo`, or (b) a restructured statement Z3 can apply, or
(c) a real per-goal best-of-N prover dispatch in `pycsl.py`. Per the extreme-rigor
doctrine this is a ROUTING condition (Alt-Ergo proves it; Rocq+Lean discharge the
induction), NOT a weakening — but the citation site must KNOW to route to Alt-Ergo.

## Proposed ergonomic fix (for the human / a future tool run)
Make PyCSL's prover dispatch a true per-goal best-of-N: run each `-P` prover
separately and accept a goal proved by ANY of them (Why3 supports this via separate
calls or a strategy). Today a goal only Alt-Ergo can discharge is masked by Z3's
Unknown when both are passed in one `why3 prove -P A -P B` call. This would let
`field_to_str_frame` (and any Alt-Ergo-only frame lemma) be cited WITHOUT a
per-file `-p` pin, removing a sharp edge from the retirement.

## Cross-validation (re-confirmed this run, compiled both provers)
- Rocq 8.20.1 `Print Assumptions field_to_str_frame`: Section Variables only
  (`rd0, rd1 : Z -> Z`), 0 Axiom/Admitted (closed under the global context).
- Lean 4.31.0 `#print axioms field_to_str_frame`: `[propext, Quot.sound]`
  (⊆ allowlist, no sorry).
