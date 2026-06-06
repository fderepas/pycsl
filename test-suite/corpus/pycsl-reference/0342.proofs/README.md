# 0342.proofs/

Companion proofs for `../0342.py` (Euclidean GCD).

`0342.py` is the canonical cross-prover reference test. Its
`#@ proof rocq <qualname>` and `#@ proof lean <qualname>` directives
(see `test-suite/annotations.md` §2.1.12) are **load-bearing**: each
emits a Why3 `axiom` block in the WhyML preamble, sourced from the
hand-curated registry in `src/pycsl/Module6_WhyMLTranspiler.py`. The
test runs under full proof (no `--no-proof`, no `\trusted`); the
Rocq/Lean theorems in this directory are the trust anchor for those
axiom statements.

## Directory layout (project convention)

```
NNNN.py                       — PyCSL reference test
NNNN.proofs/rocq/<file>.v     — Rocq proofs of the cited theorems
NNNN.proofs/lean/<file>.lean  — Lean proofs of the cited theorems
```

This is the default layout `pycsl --audit-proof` looks for. Override
with `--rocq-proofs-path DIR` / `--lean-proofs-path DIR`.

## Audit semantics

`pycsl --audit-proof NNNN.py` enforces the qualname-as-namespace
contract: a directive `#@ proof rocq Pycsl.Reference.Gcd.gcd_step`
PASSES iff some `.v` file under `rocq/` declares the theorem inside
the matching nested module path — i.e., `Module Pycsl. Module
Reference. Module Gcd. ... Theorem gcd_step ...`. The audit parses
Rocq and Lean files with a namespace-aware state machine
(`src/pycsl/audit_proof.py`); it does NOT delegate to coqc / lake.

Lean accepts both `namespace Pycsl.Reference.Gcd` (dotted) and the
equivalent `namespace Pycsl / namespace Reference / namespace Gcd`
nested form.

## Re-checking the proofs externally

```bash
# Rocq (tested against 8.20.1) — verifies the theorems are fully
# proved (no Admitted., no Axiom).
cd rocq && coqc gcd.v

# Lean 4 (tested against 4.29.1)
cd lean && lean Gcd.lean
```

Each command should exit 0 with no output. The proofs use stdlib
`Nat.gcd` lemmas — no `Admitted.`, `Abort.`, `sorry`, or user axioms.

## Why both Rocq and Lean?

The "Rocq + Lean as Cross-Validated Spec Sources" pattern: when both
`#@ proof rocq <q>` and `#@ proof lean <q>` cite the same `<q>`, the
`proof2why3 cross-check` step (when available) verifies that the two
theorem statements have equal canonical forms. Today the cross-check
is manual; the directory ships both sides so the audit can run
`--audit-proof-rocq` and `--audit-proof-lean` independently.

## Related documentation

- `docs/pycsl-concrete-syntax-reference.md` §2.1.12 — grammar
- `docs/pycsl-static-semantics-reference.md` §2.1.12 — well-formedness + audit semantics
- `docs/pycsl-translational-reference.md` §T.2.10 — Why3 axiom emission
- `docs/cross-validated-spec-sources.md` — architectural background
