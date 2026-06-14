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
| `UnixFs.Field.*` | 1 | string ↔ fixed-width null-padded byte-field codec round-trip (`field_to_str`: a name written byte-for-byte + null-terminated into a `width`-byte field, with no embedded null, decodes back exactly — the Python `struct '>Ns'` field). NOT SMT-dischargeable (proof is by string EXTENSIONALITY over Why3's axiomatic `string.String`, which E-match-explodes — ~23M-step timeout; string-codec Phase A); so it is a CITED axiom SMT only APPLIES (O(1)). Cross-validated by `test-suite/corpus/pycsl-reference/0708.proofs/{rocq,lean}/FieldToStrRoundTrip.{v,lean}` (`field_to_str` = the scan-to-first-null decode over an abstract byte-reader; round-trip proved by list extensionality + per-char `chr(code c)=c`; Rocq: closed under the global context; Lean: axioms ⊆ {propext, Quot.sound}). Foundation for re-modeling the dirent name / symlink target / file content as REAL string semantics (string-codec plan Phases B–C). |
| `UnixFs.Dir.*` | 6 | Directory-scan PRESENCE reflection (`dir_lookup ≥ 0 ↔ ∃ live slot`) + unsigned-byte inode non-negativity + ABSENCE reflection (`remove_reflects_absent`: after the live slot is zeroed and `name` lived only there, `dir_lookup < 0` — the `←`/absence half of the presence IFF specialised to an empty matches-set; remove-witness + uniqueness are explicit hypotheses) + INSERT-side uniqueness MAINTENANCE (`insert_preserves_unique`: from a disk with no duplicate live names, making one slot live with a fresh — not-already-live — name while every other slot is unchanged preserves no-duplicate-live-names; the maintenance lemma for the directory-uniqueness class invariant) + EMPTY-DISK ESTABLISHMENT (`empty_disk_slots_dead`: a zeroed block-5 region decodes to all 16 slots dead — the antecedent-discharge dual of `slot_inode_nonneg` that makes the zeroed-`Array.make` constructor witness establish the invariant VACUOUSLY) + DECODE-LOCALITY FRAME (`block5_decode_frame`: two disks agreeing on the block-5 bytes `[2560,3072)` have equal block-5 decode at every slot — lets the uniqueness invariant ride untouched through every non-block-5 disk write, since each disk-writing helper proves a disjoint byte-frame). With these two (gap-13) the class invariant is ACTIVE and PROVEN: established via `empty_disk_slots_dead`, maintained via `insert_preserves_unique` (directory mutators) + `block5_decode_frame` (non-directory writers), and the formerly-trusted `_dir_find_slot` uniqueness ensures is REMOVED — directory uniqueness is OUT of the TCB. Cross-validated by `unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/UnixDirScan{,Absent}.{v,lean}` + `InsertPreservesUnique.{v,lean}` + `EmptyDiskSlotsDead.{v,lean}` + `Block5DecodeFrame.{v,lean}` (Rocq: closed under the global context; Lean: axioms ⊆ {propext, Quot.sound}). Scan reflection is INDUCTIVE over the 16-slot loop — SMT times out (gap-9 presence / gap-11 absence); `insert_preserves_unique` is a finite 4-way case split (gap-12); `empty_disk_slots_dead` / `block5_decode_frame` are byte-local decode rewrites (gap-13), no induction. |

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

**Cautionary example — `UnixFs.Struct.i18.round_trip` / `i1a1.round_trip`** (the
os inode/direntry codec round-trip). This was first taken as a case-2 axiom: an
inline proof was attempted (a representation invariant supplying the codec's
field ranges → `_unpack_inode` field-range ensures → `_write_inode` → the full
os proof), every codec function proved *standalone* (`_unpack_inode` Valid in
12 s) but was slow in the full module (> 300 s) with the cost compounding, so
the round-trip was kept cited as the cross-validated axiom.

That was the wrong diagnosis. The body-verified os was then rebuilt with a
**defined pure-Python codec** (`_pack_inode`/`_unpack_inode` composed from the
body-verified byte leaves `_pack_uint32_be` etc.) replacing `struct.pack`. With
that codec, the round-trip axiom was discovered to be **unused**: the os's
verification conditions are return-code and structural goals that are
independent of disk *contents*, so no goal ever needs `unpack(pack(x)) == x`,
and the abstract `struct_pack_i18` the axiom constrains is never even called.
The citations were **vestigial**; removing all eight left the os fully proven
(0 unproven goals) and dropped its trusted-axiom base from three families to one
(only `Bitmap.bit_and_one_in_zero_one`).

> The lesson is the first question to ask before axiomatizing *or* proving
> inline: **is the property needed at all?** A costly inline attempt and a
> "pragmatic axiom" can both be effort spent discharging a hypothesis no goal
> consumes. Establish that a goal genuinely depends on the property before
> paying for it either way. (The `i18`/`i1a1` registry entries remain only
> because the separate `struct.pack`-based stub `src/pycsl_lib/os` still uses
> the abstract codec; the body-verified `pure_lib/os` no longer cites them.)

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
