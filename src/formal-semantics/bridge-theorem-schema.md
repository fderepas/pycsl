# Bridge theorem-schema — the richer-contracts certificate (P4)

*The formal note the richer-contracts bridge produces (`richer-contracts-bridge-plan.md` §3 P4). It states
the composition the bridge is built to deliver, its soundness, and — honestly — its measured reach on live
code. Companion to the contract-strength census (`getting-better/richer-contracts-bridge/
contract-strength-census.md`) and the coherence architecture (`the-finishable-path.md`, whose per-arm
coherence lemmas this composes with). The 3-axiom soundness ledger stays at 3; the bridge's metric is the
**footprint of `trusted_contracts_axiom`**, not the ledger count.*

## 1. The composition (the theorem-schema)

For a mirror handler method `handler_F` whose formal arm `F` has:
- a **C3 contract** proved SMT-side on the running mirror: `handler_F(args…) = emit_F(args…)` — a
  *string-builder equality* (SMT never touches semantics); and
- a **coherence lemma** proved once, Rocq/Lean-side: `eval_whyml(emit_F s) st = wp_F s st`
  (`pycsl-wp-spec.mlw` module `PyCSL_WP_Coherence` / `Phase6L_ComposeIfWhile.v`, 0 Admitted);

the two compose, **per method, mechanically**:

```
  eval_whyml( handler_F(args) ) st  =  eval_whyml( emit_F(args) ) st  =  wp_F <s> st
                                     ↑ C3 (SMT, string equality)      ↑ coherence (Rocq/Lean, once)
  ⟹  the running handler's emitted string performs the WP state transformation of arm F,
      modulo the 3-axiom ledger — a Dafny-strength per-method claim, with SMT proving only
      string-builder equalities and the *meaning* living in the machine-checked coherence lemmas.
```

**Soundness of the schema is established** (each half is machine-checked where stated) and the C3 half is
**demonstrated viable** by the S-c3 witness (`getting-better/richer-contracts-bridge/s-c3-witness.mlw`:
`ensures result = emit_F_assign s x e`, 4/4 Valid via `String.concat_assoc`, 0 axioms).

## 2. Measured reach on LIVE code (the honest status)

| Rung | Contract | Live methods achieving it |
|---|---|---|
| **C3** (`\result = emit_F_F`) | semantic; the schema above applies | **0 live** (the S-c3 witness only) |
| **C2** (structural/relational) | `wf_ir_deep` preservation; `in_emitted_fragment`; `setfold_leaf_empty` | **2** — `_subst_type_in_ir`, `collection_binder_kinds` |
| **C1** (measure/shape) | `size(\result) > 0` | **1** — `_subst_type_in_ir` (also C2) |
| **C0** (floor) | `requires True / ensures True / assigns F` | all others |

**Why C3 = 0 live (measured, P3).** Every live statement handler renders its sub-expressions and chains
`rest` through **trusted program `val`s** (`_expr_to_whyml`, `whyml_ident`, `_stmts_to_whyml`,
`_seq_init_expr`, `_coerce_to_int`), emitted as `val … : string ensures { true }` — an *arbitrary* string,
not a deterministic logic term and not in scope in a logic `ensures`. So `handler_F(args)` cannot be
*equated* to a deterministic `emit_F(args)`. The S-c3 witness proved C3 over a **logic** renderer
(`pretty_expr`) applied to a **parameter** expr; the equality does **not transfer** to a handler that
renders via a trusted program `val`. Reaching C3 on live handlers therefore requires first lifting the
**expression emitter** (`_expr_to_whyml`) itself to C3 — verified-compiler-scale work, and exactly what the
LINK-3 **coherence** lemmas already discharge once, formally (the `handle_F_code` string-parametric specs
take the *already-rendered* sub-string as a parameter with a hypothesis, mirroring the witness shape).

## 3. What the bridge therefore certifies today

- **The schema is sound and demonstrated** — where a method reaches C3, its running output provably performs
  the WP transformation modulo the 3-axiom ledger. This is the writeable Dafny-strength claim.
- **On live code, the achieved shrinkage of `trusted_contracts_axiom`'s footprint is C1/C2 on 2 methods:**
  `_subst_type_in_ir` (a real T1 substitution fold) now carries checked `size(\result) > 0` +
  `wf_ir_deep`-preservation + `in_emitted_fragment` instead of `ensures True`; `collection_binder_kinds`
  carries the relational `setfold_leaf_empty`. For those methods, `trusted_contracts_axiom` assumes strictly
  less (a checked certified-shape/relational fact, not a bare `True`).
- **C3-on-live is gated, not refuted** — it is one lift (`_expr_to_whyml` → C3) away, and that lift is the
  verified-compiler work the coherence side already covers once. Until then the semantic guarantee for the
  handler family lives on the coherence side (per-arm, formally), not per-mirror-method.

## 4. Residual trust and limits (unchanged from the plan §4/§6)

- **Ledger = 3.** All bridge additions are pure definitions + proved WhyML `lemma`s (`wf_ir_deep`, the
  concat pack, `size_pos`) or **bridge-audit obligations** (the WhyML re-statements of `emit_F_*` and
  `in_emitted_fragment`), which are *mechanically cross-checked* against the Rocq originals
  (`bin/bridge-restatement-check.sh`, PASS + fails-on-corruption) — **not** soundness axioms. No new axiom
  entered the ledger.
- **Drift** is the failure mode, not unsoundness: an enriched contract that diverged from the formal side
  would be *checked but meaningless*. Killed by the generate-don't-write generator (`bin/
  gen-bridge-contracts.py`, idempotent + lint) and the re-statement cross-check + CI round-trip
  (`bin/bridge-roundtrip.sh`).
- **Gödel/Löb unchanged.** C3 + coherence yields per-method semantic correctness *relative to* the 3-axiom
  ledger; it does not make the system certify its own soundness from nothing. The metric is footprint
  shrinkage, never ledger elimination.
- **Corpus byte-diff 0** throughout: every emitter recognizer is mirror-gated (default `["true"]`),
  verified against a worktree-at-HEAD baseline at each phase.

## 5. Bottom line

The richer-contracts bridge is **built and its rungs are proven** (S-ext export + M1 namespacing; S-c1/C1
measure; P2/C2 wf-preservation + relational + fragment-membership; S-c3/C3 semantic equality on a witness),
with the generate-don't-write + cross-check discipline making the formal↔mirror link *checked* rather than
prose. Its **live-code reach is C1/C2 on 2 methods** (a real, if small, `trusted_contracts_axiom`-footprint
shrinkage), and the full per-method Dafny-strength C3 claim is **sound, demonstrated, and gated on one
named lift** (the expression emitter), which the LINK-3 coherence layer already discharges once. That is the
strongest claim the measured facts permit, and — unlike a body-faithful `ensures` the SMT backend can never
discharge — every step of it is bounded, checked, and buildable from the certified assets already in the
tree.
