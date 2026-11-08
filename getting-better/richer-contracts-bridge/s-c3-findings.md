# S-c3 findings — richer-contracts bridge, the load-bearing spike (2026-07-09)

**Verdict: GREEN (a)** (independently re-verified: witness `emit_handler'vc` Valid, Alt-Ergo 1.5s / Z3 0.09s;
concat facts = 3 proved `lemma`s, 0 axioms; `src/pycsl` untouched; corrupted twin FAILS). **C3 is SMT-viable
directly** — the bridge's ceiling for straight-line handlers is **Dafny-parity-static**, not the per-run
fallback. SMT proves only the string-builder equality; the string's *meaning* stays proved once in Rocq/Lean.

## What was measured
- Target: the straight-line scalar-assign emission path (`f"{indent}let {x} = ref {val} in\n"`, all 4
  emit_F_assign branches). A Python f-string is left-associated appends; `emit_F_assign` is a right-
  associated concat tree — their equality is the named associativity-normalization risk.
- Witness `s-c3-witness.mlw`: a method with `ensures { result = FX.emit_F_assign s x e }` (symbolic x/e).
  **Proved best-of-N in ~0.09–1.5s** — `String.concat_assoc` (stdlib) alone discharges it; the small
  proved `concat_*` lemma pack is a stable normalization vocabulary, not strictly load-bearing. Mitigation
  (b) fragment-list and the fallback were NOT needed. Even less machinery than the plan feared.
- Non-vacuous: a one-atom-corrupted twin (`" = ref "`→`" = REF "`) with the same ensures FAILS (AE timeout /
  Z3 OOM). Ledger 3 (concat facts are `lemma`s from stdlib String axioms, not new axioms).

## Two real P3 obligations surfaced (both honest, both orthogonal to the concat risk)
1. **Atomization faithfulness.** emit_F abstracts `\n` as `constant nl`; a raw f-string fuses `"\n"` into
   its preceding literal, and Why3 string literals are opaque (`concat " in" "\n"` ≠ provably `" in\n"`). So
   the P3 spec-generator MUST atomize the mirror f-string to match emit_F's atoms. Separate from
   associativity; a generator obligation, not an SMT-viability blocker.
2. **P3 eligible population (coverage-table estimate, ~15 emitted constructs):** ~10 C3-eligible straight-
   line handlers (assign, augassign, array-set, field-assign/aug, slice-set, ghost-assign/array-set,
   expr-stmt, + trivial leaves continue/skip/return-plain; seq-assign/tuple-unpack reduce to proved
   SSeq∘SAssign). **Capped at C2:** if / while / for / whole-list seq / critical — they recurse into
   `_stmts_to_whyml` (the St_if/St_while string-theory explosion arm-coverage already moved to Rocq).

## Consolidated: all THREE gating spikes through (S-ext, S-c1, S-c3)
- **S-ext** GREEN — export + M1 namespacing feasible; extraction is a faithful WhyML RE-STATEMENT (not
  auto-extraction) ⇒ anti-drift must be a mechanized re-statement↔OCaml-extraction cross-check.
- **S-c1** GREEN — certified MEASURE/shape postconditions discharge cheaply (~0.02s); wf-PRESERVATION over
  recursive traversals is C2 (lemma-pack + requires-threading), NOT free C1.
- **S-c3** GREEN(a) — semantic C3 equality `\result = emit_F_assign` is SMT-viable directly; Dafny-parity-
  static ceiling; atomization is a P3 generator obligation.

**The bridge is feasibility-DE-RISKED.** Remaining = the ROLLOUT (P0 spec-generator + CI round-trip +
re-statement cross-check; P1 C1 measure/shape across the fold population; P2 C2 lemma-packs + generator-
emitted relational ensures + in_emitted_fragment; P3 C3 on the ~10 straight-line handlers with atomization;
P4 the contract-strength census + theorem note) — engineering scoped by these findings, not decisive
measurement. Metric = `trusted_contracts_axiom` footprint shrinkage (ledger fixed at 3).
