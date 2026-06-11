<!--
STATUS: DRAFT — follow-on gap doc from the gap-12 IMPLEMENTATION turn.
Records exactly how far the "PROVE directory uniqueness, remove it from the TCB"
goal got: Wall A LIFTED (tool), the maintenance lemma REGISTERED + dual-kernel
validated, but the CLASS-INVARIANT ACTIVATION walls on two discharge gaps. Names
the two residual walls precisely + the design each needs. NO re-trust, os kept
GREEN at the last working stage.
-->

# Gap-13 — discharge the (now-statable) directory-uniqueness class invariant

## 0. Goal (unchanged, from the user)

Directory uniqueness must be a PROVEN, maintained class invariant; the
`\trusted` uniqueness ensures on `_dir_find_slot`
(`pure_lib/os/UnixInodeFileSystem.py`) must be REMOVED. gap-12 cleared the
prerequisites; this doc records the two remaining discharge walls.

## 1. What gap-12 LANDED (committed by this turn, kept)

- **Wall A LIFTED (tool).** `src/pycsl/Module6_WhyMLTranspiler.py` now calls
  `_precompute_axiom_logic_funcs(self.ir)` BEFORE `_emit_type_decls`, and emits
  the axiom-func `val function` decls before the record type — GATED by the new
  `_class_inv_refs_axiom_func(ir)` predicate (`module6_whyml/preamble.py`). The
  gate is False for the entire existing corpus (verified: full-corpus byte-diff
  IDENTICAL, 0 differences), so emission is unchanged everywhere except a module
  whose class invariant applies an axiom func. CONFIRMED: with the uniqueness
  invariant activated, os's `__init__.mlw` declares
  `val function slot_inode/slot_name` at the top (before the record) and lowers
  the invariant to the raw bound `slot_inode disk 5 i` (no `slot_inode_3`
  mangle). The invariant is now STATABLE.
- **Maintenance lemma REGISTERED + dual-kernel validated.**
  `UnixFs.Dir.insert_preserves_unique` is in `_AXIOM_REGISTRY`
  (`module6_whyml/preamble.py`). Proofs shipped to
  `unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/InsertPreservesUnique.{v,lean}`.
  Rocq 8.20.1: `coqc` exit 0, `Print Assumptions` = Closed (only the four
  abstract Section Variables, no Axiom/Admitted). Lean 4.30.0: exit 0,
  `#print axioms` = `[propext, Quot.sound]` ⊆ allowlist, no `sorry`. Faithful
  (finite 4-way case split, no induction; says nothing about decode-vs-bytes).
- **axiom-registry.md** `UnixFs.Dir.*` count 3 → 4.

## 2. The two residual walls (why uniqueness is not yet PROVEN-from-invariant)

When the uniqueness `#@ class invariant` was ACTIVATED on
`UnixInodeFileSystem`, os dropped to **3 unproven goals** (every other VC stayed
Valid). The 3 are NOT the 7 directory mutators' insert-side maintenance — those
went through with the cited `insert_preserves_unique`. They are:

### Wall E (establishment) — the constructor proof is not vacuous

The record's `by { ... }` witness and the `_filesystem` module-global instance
both build `disk = Array.make 131072 0`. The invariant quantifies over
`slot_inode disk 5 i` / `slot_name disk 5 i`, which are **uninterpreted
`val function`s**. SMT therefore has NO fact that a zeroed disk has all 16
block-5 slots dead (`slot_inode (Array.make 131072 0) 5 i = 0`), so it cannot
discharge the establishment VC vacuously.

- VC1: `unixinodefilesystem'vc` Type invariant (the record `by`-witness) —
  **Unknown** (330688 steps).
- VC2: `_filesystem'vc` Precondition (the module-global instance) — **Unknown**
  (286703 steps).

FIX (gap-13): register a cross-validated **empty-disk-decode axiom** —
`forall disk blk k. (forall b. 512 <= b < L -> disk[b] = 0) -> slot_inode disk
blk k = 0` (or the narrower block-5 form), the dual of the existing
`slot_inode_nonneg`, asserting the abstract decode of an all-zero dirent region
is 0. With it the establishment is genuinely vacuous (all slots dead → no live
pair). Must be Rocq+Lean validated like the others (it is a faithful property of
the `_unpack_direntry` decode: zero bytes → inode field 0). This is the missing
ANTECEDENT-discharge axiom, NOT a re-trust.

### Wall M (maintenance leaks past the directory mutators)

A class invariant is a proof obligation on EVERY method with `assigns self.disk`
— not only the 7 directory mutators. Non-directory writers that never touch
block 5 (chmod via `_write_inode`, write, truncate, …) must STILL re-prove the
block-5 uniqueness invariant after their full-disk write, over the abstract
`slot_inode disk 5 i`. That balloons:

- VC3: `chmod'vc` Type invariant — **Timeout** (30.00s, 232455986 steps).

`#@ no_inline` cannot help: the obligation is inherent to the
record-with-invariant design, not a callee-inlining artifact. Trigger-tuning
(`#@ assert`/`by`) at chmod did not apply cleanly because the VC is the implicit
type-invariant re-establishment, not a user assert.

FIX (gap-13): give the non-block-5 writers a CHEAP frame that lets the invariant
ride through untouched. Options to evaluate:
1. A `_write_inode`/inode-region slot-locality frame ensures
   (`\forall k. slot_inode(self.disk, 5, k) == \old(slot_inode(self.disk, 5, k))`)
   — the inode region (bytes 512..2559) is disjoint from block 5 (bytes
   2560..3071), so an inode write leaves every block-5 decode unchanged. With
   that frame the invariant maintenance is a one-line rewrite (no balloon),
   mirroring how `_write_entry`/`_zero_entry`'s slot-locality frame already
   carries the directory mutators. EVERY `assigns self.disk` helper that does
   not write block 5 needs the analogous block-5-decode frame.
2. Alternatively, model block 5 as a SEPARATE field from the rest of the disk so
   the invariant only re-checks on block-5 writes (larger refactor; faithful but
   touches the whole model).

Option 1 is the minimal faithful path: it is the same byte-local-decode trust
class as the existing frames, and collapses VC3 to a rewrite.

## 3. State at end of the gap-12 turn

- spec-12 STATUS: IMPLEMENTED-PARTIAL.
- Wall A LIFTED; `insert_preserves_unique` registered + dual-kernel validated;
  proofs shipped; axiom-registry.md updated; full-corpus byte-diff IDENTICAL.
- Class invariant kept INACTIVE (commented, with the precise reason inline above
  the class). The 7 directory mutators' insert-side maintenance PROVED under the
  cited lemma when the invariant was active (the citations were then reverted
  along with the invariant to keep os byte-clean at the inactive stage).
- `_dir_find_slot` trusted uniqueness ensures RETAINED (clearly marked, pointer
  to this doc) — uniqueness NOT yet removed from the TCB.
- os GREEN at the inactive stage; 7/7 `formal_os_namespace.py` VALID;
  conformance 38/38; doc-coherency green.
- REMAINING for gap-13: register the empty-disk-decode axiom (Wall E) + add the
  block-5-decode frame to the non-directory `self.disk` writers (Wall M), then
  re-activate the invariant and DROP the trusted uniqueness ensures.
