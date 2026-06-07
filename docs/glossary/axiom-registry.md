# Axiom Registry

The **axiom registry** is the curated catalogue of theorem-prover-backed
axioms that PyCSL can import into a WhyML verification condition via
`#@ proof rocq <qualname>` / `#@ proof lean <qualname>` directives.

## Location

`src/pycsl/module6_whyml/preamble.py` — the `_AXIOM_REGISTRY` dict maps
each dotted qualname to its Why3 axiom body (a universal formula).

## Purpose

SMT solvers (Alt-Ergo, Z3) are decision procedures for quantifier-free
or shallow-quantifier theories. Properties that require **induction**,
**uninterpreted predicate constraints**, or **cross-function relational
reasoning** exceed their reach. The axiom registry bridges this gap by
letting the user *cite* a property proved once in a proof assistant
(Rocq and Lean, cross-validated) and injected as a trusted `axiom` into
the Why3 module preamble.

## Trust model

Every registry entry must satisfy:

1. **Paired proof** — a Rocq `.v` file AND a Lean `.lean` file prove the
   same mathematical statement (in `NNNN.proofs/{rocq,lean}/`).
2. **No extraneous axioms** — `Print Assumptions` (Rocq) and
   `#print axioms` (Lean) must show only kernel-level axioms from the
   allowlist (`proof_axiom_allowlist.py`).
3. **Cross-check** — `audit_proof.py` verifies both conditions
   automatically; a failure is a hard transpilation error.

## Current families

| Qualname prefix | Count | Domain |
|-----------------|-------|--------|
| `Pycsl.Reference.Gcd.*` | 7 | Euclidean GCD (divisibility, maximality, step) |
| `Pycsl.Reference.Perm.*` | 2 | Permutation (reflexivity, reversal) |
| `Pycsl.Reference.Json.*` | 1 | Inductive involution over recursive datatype |
| `UnixFs.Bitmap.*` | 1 | Bitwise bound (`bit_and n 1 ∈ {0,1}`) |
| `UnixFs.Struct.*` | 3 | struct.pack/unpack round-trip identity |

## Usage in contracts

```python
#@ proof rocq Pycsl.Reference.Gcd.gcd_step
#@ proof lean Pycsl.Reference.Gcd.gcd_step
```

The transpiler looks up `Pycsl.Reference.Gcd.gcd_step` in
`_AXIOM_REGISTRY`, emits the corresponding `axiom pycsl_axiom_...`
declaration in the WhyML preamble, and the SMT solver may then use it
to close verification conditions that would otherwise time out.

## See also

- [formal-test](formal-test.md) — tests that exercise axiom-backed contracts
- [proof-companion](proof-companion.md) — paired Rocq/Lean proofs
