**Trust seam** is the boundary between formally-proved and
`\trusted` portions of the PyCSL pipeline — the line above
which every claim is mechanically checked by Rocq / Lean
kernels, below which claims are accepted on reviewer
authority.

The seam's position migrates as TCB reduction proceeds. Its
current location is the IR (the Module 5 JSON boundary).

---

## What the seam does

The PyCSL pipeline is a chain:

```
Python source
   ↓ Module 1 (libcst ingest)
   ↓ Module 2 (CSL grammar parse)
   ↓ Module 3 (contract weave onto Python AST)
   ↓ Module 4 (semantic analysis + IR_well_formedness check)
   ↓
Module 5 (JSON IR emission)  ← trust seam (current)
   ↓
Module 6 (WhyML transpilation)
   ↓ wp_gen / vcg / pycsl_soundness
   ↓
.mlw → Why3 → SMT verdict
```

Everything above the seam is `\trusted reviewer:` by design
(out of formal scope). Everything below is machine-checked.

The seam concept makes the trust story explicit: a security
auditor reads `audit-plan.md` and sees exactly which claims
are kernel-proved (Tier 0a/0b — see
[trusted-computing-base.md](trusted-computing-base.md)) and
which require manual review.

## Seam trajectory across PyCSL quarters

The position of the seam moved as the formal-semantics work
progressed, each step pushing the machine-checked boundary
further up the pipeline:

| Seam position | What changed | What's above (trusted) | What's below (proved) |
|---|---|---|---|
| Module 6 opaque (the "facade") | the entire WhyML emitter was trusted | All of Modules 1-6 + emission + WhyML | Just the WP calculus and pycsl_soundness on the formal stmt model |
| Module 6 emit_stmt | `module6_encodes_mlw` decomposed into 15 per-construct theorems | Modules 1-5 + the byte-diff residue | Module 6 emit_stmt up to per-construct correspondence |
| Why3 bridge | a Why3 trust-cert serves as the witness | Modules 1-5 + the byte-diff residue | Module 6 + Why3-bridge + `why3_certificate` |
| **IR boundary (current)** | the Module 5 IR shape became machine-checked | **Modules 1-4 (Python frontend)** | **Module 5 IR shape + Module 6 + WP + soundness** |

The IR-shape correspondence verifies that Module 5's actual JSON
output matches the formal `stmt` type via `ir_to_stmt`, validated
against the byte-diff harness on the real corpus.

## Where the seam appears in the codebase

The seam is documented at three levels:

- **`src/formal-semantics/audit-plan.md`** — the canonical
  trust ledger. Section 3 enumerates every PyCSL feature
  with its current "above seam (trusted)" or "below seam
  (proved with theorem reference)" status.
- **`\trusted reviewer:` annotations** — surface-level
  markers in self-annotate mirror sources at the trust
  boundary, identifying the reviewer who vouches for the
  trusted module.
- **`pycsl_soundness` theorem** — the trust closure. Its
  assumptions (`Print Assumptions pycsl_soundness`)
  explicitly list what remains above the seam.

## Why the seam still exists

Some boundaries are deliberately above the seam:

- **Modules 1-4** — libcst, Lark, AST weaving, semantic
  analysis. Formalizing these is a research project on
  libcst + Lark, not a verification project.
- **Alt-Ergo / Z3** — `altErgoCorrect` is a separate trust
  line and stays axiomatic (Tier 1, named external axiom).
- **Why3 kernel** — the formal semantics formalizes only
  the formula evaluation subset PyCSL uses, not the full
  Why3 logic.
- **Standard library stubs** — `data/lib_stubs/<module>.py`
  contracts are `\trusted reviewer:`, Tier 2.

Further seam migration (e.g., into Module 4's semantic
analyzer) is possible but multi-quarter; the current state
is the "natural" stopping point where formalization meets
research project.

## Seam visualization

`src/formal-semantics/audit-plan.md` includes the ASCII trust
diagram. The seam in that diagram is the horizontal line
between the "machine-verified" block above and the "trusted
by design / trusted by WhyML" blocks below.

## See also

- [Trusted Computing Base](trusted-computing-base.md) — the
  tier taxonomy (0a/0b/1/2/3/4) classifying every trust
  assumption.
- [IR well-formedness](ir-well-formedness.md) — the
  predicate anchoring the current trust seam.
- [Extraction-extensional residue](extraction-extensional-residue.md)
  — the meta-level claim sitting at the seam between
  Module 6's Rocq-extracted pretty-printer and its
  Python implementation.
- `src/formal-semantics/audit-plan.md` — the canonical
  ledger of seam position per feature.
