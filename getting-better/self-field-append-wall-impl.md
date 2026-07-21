# self-field-append-wall-impl.md — implementation plan (spike-first; emission-refutation exit)

Synthesized from `self-field-append-wall.md` + `-response.md` (Gate R **CONFIRM**, 2 REFINE). The MODELING is proven
(fable `setenv_faithful.mlw`: `self._env_keys <- snoc (old self._env_keys) key` Valid, axiom-free). The M1 blast
fear is REFUTED (the facade is in NO green corpus proof). The impl make-or-break is the EMISSION: a `seq pyval`
self-field + faithful append + the fieldless-mirror retrofit, kept byte-inert by GATING.

## Design (per the fable REFINE)
- **GATE the faithful write-back on the `seq pyval` self-field case.** `self._field.append(x)` where `_field` is a
  pyval-seq self-field → `self.<field> <- snoc (old self.<field>) (<pyval-wrap x>)`. The homogeneous `array int`
  self-field appends (proc/iomod/hlib corpus) keep the CURRENT shadow-local lowering → **byte-inert** (no M1). Only
  the NEW pyval-seq-field case (the IREmitter collectors) gets the faithful write-back.
- **Retrofit the fieldless IREmitter mirror** with the needed `seq pyval` field(s) (`_final_registry` etc.) as a
  modeled record field + class invariant (the `@mutable_state` stateful-record shape), gated on a new
  `_uses_pyval_seq_field` signal → corpus + every other mirror byte-identical.
- Reuse **Phase2f** (`seq pyval` element soundness) + Why3-intrinsic `seq.Seq`/`snoc` — NO new axiom, ledger 3.

## Gate S — EMISSION make-or-break SPIKE FIRST (refutation exit)
1. Re-prove the fable model (`why3 prove -P z3 getting-better/setenv_faithful.mlw`) — reproduce Valid + axiom-free.
2. Retrofit a `seq pyval` self-field into the mirror record + emit the faithful append for a MINIMAL fixture (a
   method that appends a `{str-lit, str-var}` pyval dict to a self-field and reads it back). `pycsl <fixture>
   --keep-mlw`. Does the emitted append lower to a REAL `self.<field> <- snoc (old self.<field>) (PMap …)`
   (write-back, NOT a shadow-local), and does the file TYPECHECK + the fixture PROVE (append→read-back faithful,
   evil-twin non-vacuous)?
   - PASS → build K1 fully + K2 (converge + convert).
   - REFUTE (the fieldless-mirror seq-field retrofit won't type / forces a byte-diff on the corpus / a class-invariant
     won't discharge / the append can't gate byte-inertly) → REVERT ALL, record CERTIFIED-BOUNDARY (§ GATE-S OUTCOME)
     with the exact Why3/emit error. Do NOT grind.

## Build (only if Gate S PASSES)
- **K1 — seq-pyval self-field + faithful append emission + fixture:** the `_uses_pyval_seq_field` gate; the record
  field declaration + class invariant; the append write-back emission (statements.py ~2980/:1404 — the shadow-local
  site — gated to the pyval-seq case); a reference fixture `test-suite/corpus/pycsl-reference/0920_pyval_seq_field_
  append.<ext>` (git add -f) proving append→read-back faithfully (non-vacuous; evil-twin). Gate: fixture proves,
  corpus byte-diff 0 (gated ⇒ homogeneous appends unchanged), ledger 3. Count unchanged (infra; fixture = witness).
- **K2 — converge + convert `_collect_final_registry`:** R1 (nested `for cstmt in stmt.body` over a pyast_stmt
  LOCAL — `stmt_body` projector + propagate `_pyast_stmt_locals`) + R2 (`ast.walk(cstmt)` opaque `ast_walk:
  pyast_stmt->psl` val + loop recognition) + the K1 self-field-append + `Dict[str,PyVal]` annotation. Port verbatim,
  convert. Gate: `--fun pycsltojsonemitter___collect_final_registry` all-VCs-Valid (whole-file wedges on heavy
  Module5 → --fun authoritative per ENV note) + L3-tc ✓, fidelity 52/52 verbatim, count DOWN (1015→1014), byte-diff
  0, mutation test, ledger 3.

## Gate battery (per increment — driver-verifier FRESH)
Fidelity ∧ (whole-file proof OR --fun+wedge-note) ∧ byte-diff-0 (gated ⇒ corpus-inert; NOT M1 since gated) ∧
ledger==3 (Print Assumptions/#print axioms; reuse Phase2f) ∧ count strictly down ∧ non-vacuity (MUTATION TEST;
FIELD ACTUALLY WRITTEN BACK — grep the emitted `self.<field> <- snoc`, NOT a shadow-local; Bug-3 anti-facade).

## Honest costed scope
K1 (seq-field retrofit + append emission + fixture) is the foundation. K2 converts the first cascade collector +
banks R1/R2 (reusable for _collect_class_fields, _collect_type_params). Then the synthesize_* collectors (need
multi-arg projection + type_decls.append — a follow-on). Refutation exit at Gate S if the fieldless-mirror retrofit
walls. Corpus repair of proc argv / iomod fileio int-erasure is OPTIONAL (only to OBSERVE the effect on a green
pipeline — not required for the gated, byte-inert build).
