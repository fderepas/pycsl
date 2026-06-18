# `_write_dir_entry` 7→6 retirement — PROPOSAL + GAP (folded byte-rung maintenance axiom cross-validated; integration hits the trigger-poison wall)

DATE: 2026-06-18
LOOP: test-supervise-sl (mission: assemble the `_write_dir_entry` de-trust, prove end-to-end, STOP at proposal)
STATUS: **DOES NOT RETIRE.** The new folded maintenance axiom pair IS cross-validated
zero-TCB in BOTH provers (the load-bearing deliverable, eligible). But the os-body
integration does **not** discharge: the de-trusted `_write_dir_entry` Postcondition OOMs
and the `_blit_dir_entry` byte-blit helper's PURE-BYTE Postcondition E-match-EXPLODES
(Timeout **869,354,004 steps**) the moment the new axioms are emitted into the module —
the documented byte-keyed-trigger-poison wall, one level worse than before. Per doctrine
this is a **logged GAP routed to the human**, NOT a trusted "done". Tree reverted to clean
HEAD; the reproducible patch + the cross-validated proof sources are captured below.

## Bottom line (the mission questions)
1. **Does it retire 7→6 with both gates green? NO.** The `#@ \trusted` directive count
   drops 7→6 syntactically (the directive was removed from `_write_dir_entry`), BUT the
   body does not VERIFY — so it is a REGRESSION, not a retirement. A de-trust whose body
   reds the gate is not a closure (formal-test-consequence / safe-vs-risky doctrine).
2. **Is the new axiom cross-validated zero-TCB? YES.** `insert_preserves_dir_invariant_blit`
   and `zero_preserves_dir_invariant_blit` compile in BOTH Rocq and Lean over the same
   concrete model as the landed keystones (FieldToStrFrame + SlotInodeByteDecode +
   DirInvariantMaintenance), with clean assumptions:
   - Rocq `Print Assumptions` (both): **Section Variables only** (`rd : disk -> Z -> Z`,
     `disk : Type`) — Closed under the global context, 0 Axiom/Admitted.
   - Lean `#print axioms` (both): **`[propext, Quot.sound]`** ⊆ allowlist, no `sorry`.
3. **The precise wall (below):** the folded axiom's byte-keyed trigger `[d1[2560 + 32*s]]`
   is NOT narrow enough — it E-matches against the ubiquitous block-5 byte reads in the
   byte-blit helper `_blit_dir_entry` (`self.dir[off]`, `self.dir[2560+b]`), dragging the
   abstract slot_inode/slot_name/uniq/slots_lt32 web into that helper's PURE-BYTE VC. So
   emitting the axiom poisons a sibling mutator's previously-clean byte postcondition.

## The new axiom (the eligible, cross-validated deliverable)

WhyML form (added to `src/pycsl/module6_whyml/preamble.py` `_AXIOM_REGISTRY`):

```
UnixFs.Dir.insert_preserves_dir_invariant_blit :
  forall d0 d1 : array int, s b0 b1 : int [d1[2560 + 32 * s]].
    uniq d0 -> slots_lt32 d0 -> 0 <= s < 16 ->
    d1[2560 + 32 * s] = b0 -> d1[2560 + 32 * s + 1] = b1 ->
    256 * b0 + b1 <> 0 -> 256 * b0 + b1 < 32 ->
    ( forall b : int. 0 <= b < 512 ->
        (b < 32 * s \/ 32 * s + 32 <= b) -> d1[2560 + b] = d0[2560 + b] ) ->
    ( forall k : int. 0 <= k < 16 ->
        slot_inode d0 5 k <> 0 -> slot_inode d0 5 k < 32 ->
        slot_name d0 5 k <> slot_name d1 5 s ) ->
    ( slot_inode d1 5 s = 256 * b0 + b1
      /\ ( forall k : int. 0 <= k < 16 -> k <> s ->
             slot_inode d1 5 k = slot_inode d0 5 k /\
             slot_name  d1 5 k = slot_name  d0 5 k )
      /\ uniq d1 /\ slots_lt32 d1 )

UnixFs.Dir.zero_preserves_dir_invariant_blit :
  forall d0 d1 : array int, s : int [d1[2560 + 32 * s]].
    uniq d0 -> slots_lt32 d0 -> 0 <= s < 16 ->
    d1[2560 + 32 * s] = 0 -> d1[2560 + 32 * s + 1] = 0 ->
    ( forall b : int. 0 <= b < 512 ->
        (b < 32 * s \/ 32 * s + 32 <= b) -> d1[2560 + b] = d0[2560 + b] ) ->
    ( slot_inode d1 5 s = 0
      /\ ( forall k : int. 0 <= k < 16 -> k <> s ->
             slot_inode d1 5 k = slot_inode d0 5 k /\
             slot_name  d1 5 k = slot_name  d0 5 k )
      /\ uniq d1 /\ slots_lt32 d1 )
```

**The fold** (the doctrine-prescribed shape, 20260618-2030 §"the EXACT human-gated lemma
to finish"): the hypotheses are PURE BYTES (the two blitted inode bytes of slot s + a
byte-region frame: every block-5 byte OUTSIDE slot s's 32-byte window agrees with the
pre-state) plus the EEXIST freshness guard; the conclusion is the FULL conjunction
(slot VALUE decode + slot-locality FRAME for k≠s + uniq + slots_lt32). The byte→slot
decode rung (slot_inode_byte_decode for the value; field_to_str_frame over the disjoint
window for the per-slot frame) is discharged INSIDE the lemma, so — in principle — the os
body provides only byte facts and never materializes a slot atom.

Cross-validated proofs (re-verified this run from the in-tree location):
`test-suite/corpus/pycsl-reference/0715.proofs/{rocq,lean}/DirBlitInvariant.{v,lean}`.

The proof's heart is `slot_frame_of_region` (proved ONCE, applied opaquely by both
theorems so the heavy `field_to_str_frame` term is kernel-checked once): slot k's 32-byte
window (k≠s, both in range) is disjoint from slot s's window, hence entirely inside the
framed block-5 region, so `slot_inode`/`slot_name` at k are preserved; the value comes
from the two blitted bytes; uniq/slots_lt32 then follow by the DirInvariantMaintenance
case split. The Rocq proof initially OOM'd at `Qed` because of a `repeat split; try
assumption` that attempted to unify the frame conjunct against the huge `Hframe`
hypothesis — replaced with an explicit `exact (conj ... )`, which compiles in ~2.6s.

### Print Assumptions / #print axioms (verbatim, this run)
```
# Rocq (both theorems):
Section Variables:
rd  : disk -> Z -> Z
disk : Type
# Lean:
'UnixFs.Dir.insert_preserves_dir_invariant_blit' depends on axioms: [propext, Quot.sound]
'UnixFs.Dir.zero_preserves_dir_invariant_blit' depends on axioms: [propext, Quot.sound]
```

## The integration that was tried (in the captured patch)
`_write_dir_entry` (block 5 lives in `self.dir`):
- de-trusted (the `#@ \trusted reviewer: dirscan-fidelity` removed);
- body: `self._blit_dir_entry(entry_offset, inode_num, name)` (a `#@ sibling_concrete`
  byte-only helper with PURE-BYTE ensures: `self.dir[off]==inode_num//256`,
  `self.dir[off+1]==inode_num%256`, the name-field bytes, and the byte frame
  `∀b. (b<off ∨ off+32≤b) ⟹ self.dir[b]==\old(self.dir[b])`);
- then a folded byte-region-frame `#@ assert
  ∀b. 0≤b<512 ∧ (b<32*slot ∨ 32*slot+32≤b) ⟹ self.dir[2560+b]==\old(self.dir[2560+b])`;
- a new `#@ requires` freshness guard (the EEXIST fact live callers establish);
- cites `#@ proof rocq/lean insert/zero_preserves_dir_invariant_blit`.

## The PRECISE wall (the human-gated residual / GAP)

Full body gate (`PYTHONHASHSEED=0 .venv/bin/python3 src/pycsl/pycsl.py
pure_lib/os/UnixInodeFileSystem.py`):
- BASELINE (HEAD, `_write_dir_entry` trusted): **2–3 goals** remain (aggregate
  non-deterministic noise: `sys_rename` Assertion Timeout ~4.6M; `_unpack_direntry`
  Precondition Unknown — PRE-EXISTING, unrelated).
- DE-TRUST (this run): **3 goals remain**, attributed:
  1. **`_blit_dir_entry` Postcondition — Timeout 869,354,004 steps** (and Out-of-memory
     across provers). THE NEW EXPLOSION. `_blit_dir_entry`'s ensures are PURE BYTES (no
     slot atoms), yet its postcondition explodes — because once the two new axioms are
     EMITTED (cited by the sibling `_write_dir_entry`), their byte-keyed trigger
     `[d1[2560 + 32*s]]` E-matches the helper's block-5 byte reads and pulls the abstract
     slot_inode/slot_name/uniq/slots_lt32 axiom web into the helper's byte VC.
  2. **`_write_dir_entry` Postcondition — Out of memory.** The slot_name VALUE
     postcondition (`slot_name(self.dir,5,slot)==name`) still needs the string round-trip
     materialized to bridge the freshness `requires` (`slot_name(...,k)!=name`) to the
     axiom's antecedent (`slot_name d0 5 k <> slot_name d1 5 s`) — re-introducing the slot
     atom alongside the byte terms.
  3. `sys_rename` Assertion Timeout 7.4M — PRE-EXISTING baseline noise.

So the de-trust adds **2 NEW unproven goals** (a regression) and does not retire.

### Root cause (catalog-B): the byte-keyed trigger is still too broad
The fold was designed so "no byte term and no slot atom coexist in a body VC." It achieves
that for the *abstract-symbol* trigger (the axiom does NOT key on `uniq d`/`slot_inode d
blk k`). BUT its byte key `[d1[2560 + 32 * s]]` matches the SHAPE `disk[2560 + <expr>]`,
which is exactly the index every block-5 byte-blit produces. So the axiom fires inside
`_blit_dir_entry` itself and inside any block-5 mutator, instantiating its abstract-slot
conclusion (and the nested `forall b`/`forall k` antecedents) into those VCs — the
documented "keystone emission poisons every directory mutator's invariant VC" failure,
now amplified by the conclusion's four-way conjunction over the slot web. This is the
same class as catalog-B's "Materializing a byte VALUE term to fire a keystone RE-triggers
the explosion (the byte term and the slot atoms cannot coexist)" — the fold moved the
coexistence from the *body assert* to the *emitted-axiom instantiation*, but did not
eliminate it.

### What a future session needs (NOT autonomous — human-gated)
The fold is correct logic (cross-validated). The remaining engineering is making its
WhyML TRIGGER fire EXACTLY ONCE, only at the genuine `_write_dir_entry`/`_zero_entry`
post-blit site, and never in `_blit_dir_entry` or other block-5 touchers. Candidate
directions (each a human TCB / tooling decision, none a `\trusted`):
- a trigger keyed on a UNIQUE marker term present only at the real apply site (e.g. an
  uninterpreted `dir_blit_marker d1 s` atom the body asserts once, à la gap-17's
  `block_content_eq` folded atom) so the axiom cannot match raw `disk[2560+...]` reads;
- keep `_blit_dir_entry` OFF `sibling_concrete` (a clean abstract `val`) so its byte
  reads never appear in a caller VC alongside the axiom — but that re-opens the
  field-referencing-ensures propagation gap (20260618-1640);
- prove `_blit_dir_entry` in ISOLATION with the axioms NOT emitted (split the module so
  the byte helper and the cited mutators don't share a preamble) — a packaging change.

## Gating evidence
- New-axiom cross-validation: Rocq Section-Variables-only (both); Lean `[propext,
  Quot.sound]` (both). RE-VERIFIED from `0715.proofs/{rocq,lean}/`.
- Emission-gating (corpus-inert when UNCITED): emitting `pure_lib/os/UnixInodeFileSystem.py`
  with the registry entries present but NOT cited → the two axiom names are ABSENT from
  the emitted `.mlw` (0 matches). The poison appears ONLY once `_write_dir_entry` cites
  them — i.e. the entries are inert until cited, but the citation's blast radius is the
  whole module preamble (the wall).
- Body gate: 2–3 (baseline) → 3 WITH 2 new explosive goals (`_blit_dir_entry` 869M-step
  Timeout/OOM, `_write_dir_entry` OOM). NOT ≤ baseline → NOT shippable.
- `__init__` gate + full-corpus byte-diff NOT run to completion (the body gate already
  fails decisively — the retirement is dead at the body gate; running the downstream
  gates would not change the verdict).

## Patch + reproduction
- Self-contained patch (the de-trust + registry entries + proof sources):
  `getting-better/PROPOSAL-write-dir-entry-detrust.patch` (`git apply` from repo root).
- Cross-validated proof sources are inside the patch
  (`test-suite/corpus/pycsl-reference/0715.proofs/{rocq,lean}/DirBlitInvariant.{v,lean}`).

## TCB statement
The folded axiom pair, if it could be made to integrate, would ADD a NEW emitted
cross-validated axiom that a LIVE os trust would depend on — a human TCB decision (the
user's explicit sign-off), never the loop's or the parent's to ship autonomously. As it
stands the integration does not even reach a green gate, so there is nothing to ship: the
deliverable is this GAP write-up + the cross-validated axiom (banked for the trigger-
narrowing follow-on) + the reproducible patch. The tree is reverted to clean HEAD.
