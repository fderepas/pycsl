**formula_rep** is Why3's denotational evaluation predicate for
closed monomorphic formulas, formalized by Cohen & Jourdan-Fonseca
in their POPL'24 paper "A Mechanized Theory of Why3 Logic".

---

## Why formula_rep matters in PyCSL

PyCSL's verification chain has to bridge from Why3's "Valid" verdict
(an external trust statement about the prover) to PyCSL's denotational
semantics (`eval_vc_formula`, a Coq predicate). The bridge requires a
shared semantic notion of what a Why3 formula MEANS — `formula_rep`
provides exactly that.

For closed monomorphic formulas (the integer-arithmetic fragment
PyCSL uses for VCs), `formula_rep` reduces formula validity to a
boolean predicate on a single canonical interpretation
(`closed_satisfies_rep` in the Cohen & Jourdan-Fonseca formalization,
`Logic.v:151`). This means "Why3 says formula f is valid" can be
formally reified as "`formula_rep ... f = true`" — and, in turn,
related back to PyCSL's `eval_vc_formula`.

## How it appears in the PyCSL trust chain

Post-Q3 Sub-β (2026-05-29), the Rocq side of the chain does NOT
import `formula_rep` directly into the main build. Instead, the
`why3_certificate` type (Phase6j_Why3Trust.v) is defined as the
witness type — a function from VC indices to `eval_vc_formula`
proofs. Constructing such a certificate is what `Why3Trust.check`
(in Lean) does after invoking the Why3 binary externally; it
parses "Valid" verdicts and reifies them into Coq evidence.

A heavier-import standalone proof exists in
`Phase6m_VcgSemBridge_Rocq9.v` that does pull in `formula_rep`
from the why3-semantics library to give an alternative grounding
for the trust line — useful as documentation that the cert-as-
witness design is consistent with Why3's formal semantics.

## See also

- [Trusted Computing Base](trusted-computing-base.md) — where
  `formula_rep` sits in the overall PyCSL TCB diagram.
- [Verification condition](verification-condition.md) — the
  inputs `formula_rep` evaluates.
- [Theorem prover](theorem-prover.md) and [SMT solver](smt-solver.md) —
  the external tools whose verdicts `formula_rep` formally interprets.
- Cohen, R. and Jourdan-Fonseca, C. "A Mechanized Theory of Why3
  Logic." POPL 2024.
