# Audit-anchor stubs for self-annotation citations

This directory and its siblings (`Module4_SemanticAnalyzer.proofs/`,
`Module5_IREmitter.proofs/`, `module6_whyml/preamble.proofs/`) exist
to satisfy `pycsl --audit-proof` for the `#@ proof rocq` /
`#@ proof lean` citations on the self-annotated modules.

## What's NOT here

These stubs are **not** the real trust chain. The actual
formal-semantics proofs live at:

- Rocq: `src/formal-semantics/rocq/Phase*.v`
- Lean: `src/formal-semantics/lean/PyCSL/*.lean`

Each stub file's header points at the upstream source line.

## Why stubs are needed

The audit (`src/pycsl/audit_proof.py`) is a namespace-aware
presence check: for a citation `Phase5b_Soundness.pycsl_soundness`,
it looks for a `.v` file declaring `Theorem pycsl_soundness` inside
a wrapping `Module Phase5b_Soundness. ... End Phase5b_Soundness.`
The formal-semantics files use Coq/Lean's implicit
file-as-module/namespace convention (no explicit wrapper). The
stubs bridge that gap.

## Stub semantics

Each stub:

- Declares the cited theorem name inside the cited module/namespace.
- Uses `True` as the statement and `trivial` as the proof — the
  audit checks declaration presence, not statement content.
- Is **not** compiled. No `_CoqProject` / `lakefile.lean` includes
  these directories. Adding them to a build target would be a bug:
  they would conflict with the real upstream theorems' statements.

## Trust-chain reference

See `closer-to-code-execution-status.md` item 48 and
`self-annot-2.md` §"CC.4 citation map" for the full trust-chain
documentation. The audit's role is to ensure that every citation
points at *some* declaration with the right name — a sanity check
against typos and stale citations, not a soundness proof.
