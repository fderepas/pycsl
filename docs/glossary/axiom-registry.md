# Axiom Registry

The **axiom registry** is the curated catalogue of theorem-prover-backed
axioms that PyCSL can import into a WhyML verification condition via
`#@ proof rocq <qualname>` / `#@ proof lean <qualname>` directives.

## Location

`src/pycsl/module6_whyml/preamble.py` — the `_AXIOM_REGISTRY` dict maps
each dotted qualname to its Why3 axiom body (a universal formula).

## Purpose

The SMT solvers (Alt-Ergo 2.6.2, Z3 4.13.3) combine theory decision
procedures with trigger-based quantifier instantiation (E-matching).
Properties that require **induction**, **uninterpreted predicate
constraints**, or **cross-function relational reasoning** lie outside
what E-matching can reach within a per-goal time budget. The axiom
registry bridges this gap by letting the user *cite* a property proved
once in a proof assistant (Rocq and Lean, cross-validated, offline) and
injected as an `axiom` into the Why3 module preamble, where it becomes a
hypothesis in scope for every goal in the module.

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

## When to axiomatize (vs prove inline)

Citing a cross-validated axiom is **sound** (the property is proved, just in a
proof assistant rather than discharged by the SMT backend), but it moves the
property's proof out of the SMT-checked perimeter. Prefer an **inline proof**
(letting Alt-Ergo/Z3 discharge the VC) when it is affordable; reach for the
registry in two cases:

1. **Beyond SMT reach** — the original purpose: properties needing induction,
   uninterpreted-predicate constraints, or cross-function relational reasoning
   (GCD maximality, the JSON involution, the bitwise bound). No per-goal SMT
   time budget closes these.

2. **Proof-cost-bound in aggregate** — a property that proves *standalone* in
   seconds but is slow or intractable *in context*, and whose cost *compounds*
   across a chain of dependent functions. The whole is unaffordable even though
   each part is provable.

**Worked example — `UnixFs.Struct.i18.round_trip` / `i1a1.round_trip`** (the os
inode/direntry codec round-trip, decided 2026-06-09). Proving it inline was
attempted end-to-end (a representation invariant supplying the codec's field
ranges → `_unpack_inode` field-range ensures → `_write_inode` → the full os
proof). Every mechanism was validated and every codec function proved
*standalone* (`_pack_inode` Valid in minutes, `_unpack_inode` Valid in 12 s),
but in the full module each was slow or returned Unknown/Timeout
(`_unpack_inode` > 300 s), and the cost **compounded** across the chain — each
step a 300 s–1200 s proof, several chained. The inline proof is therefore
**proof-cost-bound in aggregate**, not mechanism-limited. The round-trip stays
cited as the cross-validated axiom; the os holds its proven-goal count without
the inline blow-up.

> The axiom is the *pragmatic, sound* resting point — not a concession that the
> property is unprovable. Revisit case (2) only with a larger solver budget
> (`--timelimit`) or a faster prover, as a dedicated effort.

A case (2) axiom is still held to the full [trust model](#trust-model): a paired
Rocq+Lean proof of the *same* statement, no extraneous axioms, `audit_proof.py`
cross-check. The reason for citing it differs (aggregate cost, not SMT
incapacity); the soundness bar does not.

## Usage in contracts

```python
#@ proof rocq Pycsl.Reference.Gcd.gcd_step
#@ proof lean Pycsl.Reference.Gcd.gcd_step
```

The transpiler looks up `Pycsl.Reference.Gcd.gcd_step` in
`_AXIOM_REGISTRY`, emits the corresponding `axiom pycsl_axiom_...`
declaration in the WhyML preamble, and Alt-Ergo/Z3 may then instantiate
it (via E-matching) to discharge verification conditions that would
otherwise return Unknown or Timeout.

## See also

- [formal-test](formal-test.md) — tests that exercise axiom-backed contracts
- [proof-companion](proof-companion.md) — paired Rocq/Lean proofs
