<!--
STATUS: DRAFT — gap doc for the STDLIB-AGENT turn (convergence loop, gap-12).
Names the precise universally-quantified maintenance lemma (+ Rocq/Lean proof
sketch) AND the prerequisite TOOL change required to make the os directory-
uniqueness CLASS INVARIANT statable and its preservation discharged, so the
trusted uniqueness ensures on `_dir_find_slot` becomes PROVEN-from-invariant.
NO axioms registered, NO src/pycsl edits, NO git operations in this turn.
-->

# Gap-12 — replace the trusted directory-UNIQUENESS ensures with a PROVEN class invariant

## 0. Goal (from the user)

Directory uniqueness must be PROVEN as a maintained class invariant, NOT trusted.
Today `pure_lib/os/UnixInodeFileSystem.py` `_dir_find_slot` carries (under
`#@ \trusted reviewer: dirscan-fidelity`) a uniqueness ensures:

```
#@ ensures \forall k: int; (0 <= k and k < 16 and k != \result
        and slot_name(self.disk, block_num, k) == pathname)
        ==> slot_inode(self.disk, block_num, k) == 0
```

asserting "block 5 never holds two live slots with the same name". The END STATE
the user wants: this clause FOLLOWS from a maintained class invariant over the
registered `slot_inode`/`slot_name` symbols, removing uniqueness from the TCB.
(The byte-decode `\result` ↔ disk fidelity — the first two ensures — may stay
trusted as before; only UNIQUENESS must become proven.)

## 1. What landed this turn (the strongest GREEN form)

The model already carries everything §3a/§3b of `11-1219-convergence-spec-11.md`
called for:
- `_zero_entry` (`UnixInodeFileSystem.py`, the REMOVE primitive) with the trusted
  remove-witness `slot_inode(...slot)==0` AND the slot-locality frame ensures
  (`\forall k != slot. slot_inode/slot_name unchanged`).
- `_write_entry` with the same slot-locality frame ensures.
- EEXIST guards on every adder (`sys_mkdir`, `sys_link` (newpath), `sys_open`
  O_CREAT, `sys_symlink`, `sys_creat`): each REJECTS a name already live before
  writing.
- `remove_reflects_absent` registered; the 7/7 `formal_os_namespace.py`
  consequences VALID through the public API.

The INTENDED uniqueness class invariant is written (as commented WhyML) above the
`UnixInodeFileSystem` class. It is **NOT statable today** (see §2). The trusted
uniqueness ensures on `_dir_find_slot` is therefore RETAINED, but now CLEARLY
MARKED `*** STILL TRUSTED — PENDING the proven class invariant ***` with a
pointer to this doc. os stays GREEN (1191 VCs), 7/7 namespace VALID, conformance
38/38, byte-diff identical.

## 2. The TWO walls (why uniqueness is not yet proven)

### Wall A — TOOL: the class invariant cannot even be STATED (blocking, src/pycsl)

The intended invariant, over the registered `UnixFs.Dir.*` abstract symbols:

```
#@ class invariant \forall i: int; \forall j: int;
     (0 <= i and i < 16 and 0 <= j and j < 16
      and slot_inode(self.disk, 5, i) != 0 and slot_inode(self.disk, 5, i) < 32
      and slot_inode(self.disk, 5, j) != 0 and slot_inode(self.disk, 5, j) < 32
      and slot_name(self.disk, 5, i) == slot_name(self.disk, 5, j)) ==> i == j
```

does NOT lower. The class-invariant emission path
(`src/pycsl/module6_whyml/preamble.py`, the loop at ~line 1328 that calls
`self._expr_to_whyml(inv, set(), invariant_ctx=True)`) does NOT resolve
`_AXIOM_FUNCTIONS` symbols. It mangles `slot_inode`/`slot_name` to UNBOUND
`slot_inode_3`/`slot_name_3`, producing:

```
File "...__init__.mlw", line 43: unbound function or predicate symbol 'slot_inode_3'
```

Two sub-problems, both in `module6_whyml/preamble.py` (tool-agent territory —
forbidden to STDLIB-AGENT):
1. **Symbol resolution.** `_expr_to_whyml(..., invariant_ctx=True)` must recognise
   `slot_inode`/`slot_name`/`dir_lookup` (the `_AXIOM_FUNCTIONS["UnixFs.Dir."]`
   logic symbols) as those `val function`s — the SAME recognition the method-
   ensures lowering already has — instead of treating them as unknown names and
   uniquifying with a `_<n>` suffix. (No existing class invariant in the repo
   calls an abstract axiom function; this path has never had to.)
2. **Declaration ordering.** The abstract `val function slot_inode/slot_name`
   decls are emitted AFTER the record `type unixinodefilesystem = { ... }
   invariant { ... }` block. Even with (1) fixed, the invariant references symbols
   declared later in the file. The `val function` decls for cited
   `_AXIOM_FUNCTIONS` (UnixFs.Dir.*) must be emitted BEFORE the record/invariant
   block (or the invariant must be attached after the decls).

Until Wall A is fixed, uniqueness CANNOT be expressed as a class invariant in
PyCSL, so it cannot be proven-from-invariant regardless of SMT power.

### Wall B — SMT: invariant PRESERVATION balloons (the §3c balloon)

Even once Wall A is lifted, proving the invariant is PRESERVED by each mutator is
quantified+inductive over the 16 slots against the E-matching surface that
already forced `#@ no_inline` + entry-write-last to keep os GREEN (gap-9/§3c).
The adders write one live slot guarded by an EEXIST check; the removers clear one
slot. In both cases the OTHER-slot decodes are carried by `_write_entry`/
`_zero_entry`'s slot-locality frame ensures (already present), but stitching
"the new live name differs from all 16 existing live names ⟹ no new duplicate
pair (i,j)" is the inductive scan-uniqueness fact below. Expect Alt-Ergo/Z3
Timeout; do NOT re-trust — register the lemma.

## 3. The PRECISE universally-quantified maintenance lemma (for Rocq + Lean)

Register `UnixFs.Dir.insert_preserves_unique` in `_AXIOM_REGISTRY` (reuses the
existing `slot_inode`/`slot_name` symbols; no new `_AXIOM_FUNCTIONS` entry). It
is the INSERT-side companion of `remove_reflects_absent`, stated as: if the
no-duplicate-live-names invariant holds, and we make slot `s` live with a name
`nm` that was NOT already present among the live slots, the invariant still holds.
(The REMOVE side — clearing a slot trivially preserves uniqueness — does not need
its own axiom: dropping a live slot can only shrink the set of live pairs, and is
discharged from the slot-locality frame + the invariant on `\old`.)

### 3.1 WhyML statement (for `_AXIOM_REGISTRY`)

A "unique" predicate over the 16 live slots, and the preservation lemma phrased
over the pre-write decode `si0`/`sn0` and the post-write decode `si1`/`sn1` that
agree everywhere except slot `s`, where `s` becomes live with name `nm`:

```
"UnixFs.Dir.insert_preserves_unique":
  "forall si0 sn0 : int -> int. (* abstract per-slot decode, pre-write  *)
   forall nmf : int -> int.     (* slot_name as index-keyed, pre-write  *)
   ...
```

In the model's actual signature the decode is `slot_inode disk blk k`. The
faithful WhyML, over two disks `d0` (pre) and `d1` (post) that the slot-locality
frame relates, blk fixed = 5:

```
"UnixFs.Dir.insert_preserves_unique":
  "forall d0 : array int. forall d1 : array int. forall blk : int.
   forall s : int. forall nm : string.
   ( forall j : int. 0 <= j < 16 -> slot_inode d0 blk j >= 0 ) ->
   ( 0 <= s < 16 ) ->
   (* invariant holds before the write *)
   ( forall i j : int. 0 <= i < 16 -> 0 <= j < 16 ->
        slot_inode d0 blk i <> 0 -> slot_inode d0 blk i < 32 ->
        slot_inode d0 blk j <> 0 -> slot_inode d0 blk j < 32 ->
        slot_name d0 blk i = slot_name d0 blk j -> i = j ) ->
   (* nm is NOT already live before the write (the EEXIST guard) *)
   ( forall k : int. 0 <= k < 16 ->
        slot_inode d0 blk k <> 0 -> slot_inode d0 blk k < 32 ->
        slot_name d0 blk k <> nm ) ->
   (* slot-locality: d1 agrees with d0 off s *)
   ( forall k : int. 0 <= k < 16 -> k <> s ->
        slot_inode d1 blk k = slot_inode d0 blk k /\
        slot_name  d1 blk k = slot_name  d0 blk k ) ->
   (* the write made s live with name nm *)
   ( slot_inode d1 blk s <> 0 -> slot_inode d1 blk s < 32 ) ->
   ( slot_name  d1 blk s = nm ) ->
   (* THEN the invariant is preserved on d1 *)
   ( forall i j : int. 0 <= i < 16 -> 0 <= j < 16 ->
        slot_inode d1 blk i <> 0 -> slot_inode d1 blk i < 32 ->
        slot_inode d1 blk j <> 0 -> slot_inode d1 blk j < 32 ->
        slot_name d1 blk i = slot_name d1 blk j -> i = j )"
```

This is FAITHFUL (not over-strong): it asserts only the structural fact that
inserting a fresh (not-already-live) name at one slot, with all other slots
unchanged, cannot create a duplicate-live-name pair. The remover side
(clear slot ⟹ preserve) is provable directly in WhyML from the same antecedents
(d1 agrees with d0 off s; slot s dead on d1) without an axiom.

### 3.2 Rocq proof sketch (same shape as UnixDirScanAbsent.v)

Reuse the `Section Scan` framing of
`unix-filesystem/UnixInodeFileSystem.proofs/rocq/UnixDirScanAbsent.v`
(Variables `disk`, `name_t`, `slot_inode`, `slot_name`, `eqn`; Hypothesis
`slot_inode_nonneg`). NO induction over the scan is needed — the lemma is a
direct case analysis over the pair (i,j):

```coq
Theorem insert_preserves_unique :
  forall (d0 d1 : disk) (blk s : Z) (nm : name_t),
    (forall j, 0 <= slot_inode d0 blk j) ->
    0 <= s < 16 ->
    (forall i j, 0 <= i < 16 -> 0 <= j < 16 ->
        slot_inode d0 blk i <> 0 -> slot_inode d0 blk i < 32 ->
        slot_inode d0 blk j <> 0 -> slot_inode d0 blk j < 32 ->
        slot_name d0 blk i = slot_name d0 blk j -> i = j) ->
    (forall k, 0 <= k < 16 ->
        slot_inode d0 blk k <> 0 -> slot_inode d0 blk k < 32 ->
        slot_name d0 blk k <> nm) ->
    (forall k, 0 <= k < 16 -> k <> s ->
        slot_inode d1 blk k = slot_inode d0 blk k /\
        slot_name  d1 blk k = slot_name  d0 blk k) ->
    slot_name d1 blk s = nm ->
    (forall i j, 0 <= i < 16 -> 0 <= j < 16 ->
        slot_inode d1 blk i <> 0 -> slot_inode d1 blk i < 32 ->
        slot_inode d1 blk j <> 0 -> slot_inode d1 blk j < 32 ->
        slot_name d1 blk i = slot_name d1 blk j -> i = j).
Proof.
  intros d0 d1 blk s nm Hnn Hs Hinv0 Hfresh Hframe Hsnm i j Hi Hj Hil Hib Hjl Hjb Hnameq.
  (* Case split each of i,j against s using Z.eq_dec, 4 cases. *)
  destruct (Z.eq_dec i s) as [Eis|Nis]; destruct (Z.eq_dec j s) as [Ejs|Njs].
  - lia.                                   (* i=s, j=s ⟹ i=j *)
  - (* i=s (name nm), j<>s: j is live on d0 (Hframe), name(j)=nm,
       contradicts Hfresh that nm is not live on d0. *)
    exfalso. subst i.
    destruct (Hframe j Hj Njs) as [Hij Hnj].
    apply (Hfresh j Hj); rewrite Hij; try assumption.
    rewrite <- Hnj. rewrite <- Hnameq. exact Hsnm.   (* slot_name d0 blk j = nm *)
  - (* symmetric: j=s, i<>s. *)
    exfalso. subst j.
    destruct (Hframe i Hi Nis) as [Hii Hni].
    apply (Hfresh i Hi); rewrite Hii; try assumption.
    rewrite <- Hni. rewrite Hnameq. exact Hsnm.
  - (* i<>s, j<>s: both decodes equal d0's (Hframe), so Hinv0 applies. *)
    destruct (Hframe i Hi Nis) as [Hii Hni].
    destruct (Hframe j Hj Njs) as [Hij Hnj].
    apply (Hinv0 i j Hi Hj);
      [ rewrite Hii; assumption .. | ];
      rewrite Hni, Hnj; exact Hnameq.
Qed.
```

Termination/soundness: no `Fixpoint`, no `Admitted`, no `Axiom` — a finite case
split discharged by `lia` and rewriting under the slot-locality frame. Expect
`Print Assumptions insert_preserves_unique` = Closed under the global context.

### 3.3 Lean 4 sketch (mirror of UnixDirScanAbsent.lean)

Same statement in a `namespace UnixFs.Dir` `section` with `variable`s
`slot_inode`/`slot_name`; proof by `rcases (eq_or_ne i s)` / `(eq_or_ne j s)`,
the cross cases closed by the freshness hypothesis applied to the framed slot,
the off-diagonal case by `Hinv0`, integers by `omega`. Expect
`#print axioms` ⊆ {propext, Quot.sound}, no `sorry`.

## 4. Integration (after Wall A tool fix + lemma registered)

1. Tool-agent fixes Wall A (symbol resolution + decl ordering for
   `_AXIOM_FUNCTIONS` symbols in class-invariant emission).
2. Tool-agent registers `UnixFs.Dir.insert_preserves_unique` (§3.1) after the
   dual-kernel gate (Rocq Closed, Lean ⊆ {propext, Quot.sound}).
3. STDLIB-AGENT uncomments the class invariant above `UnixInodeFileSystem`
   (§2 Wall A block). `_format_disk` establishes it vacuously (slots 0,1 dead).
4. Each adder cites `insert_preserves_unique` (its EEXIST guard supplies the
   "nm not already live" hypothesis; `_write_entry`'s slot-locality supplies the
   frame). Each remover preserves it directly from the slot-locality frame +
   the invariant on `\old` (clearing a slot only shrinks the live set).
5. DROP the trusted uniqueness ensures (3rd `#@ ensures`) from `_dir_find_slot`;
   its callers (the removers) read uniqueness off the now-proven class invariant
   at the removal site. Uniqueness leaves the TCB.
6. Re-gate: os GREEN, 7/7 namespace VALID, byte-diff identical, conformance
   38/38, doc-coherency green. (Add a `glossary/axiom-registry.md` +
   `docs/pycsl-axiom-plumbing-internals.md` entry for the new axiom.)

## 5. State at end of this turn

- Invariant STATED (as the intended, commented WhyML) above
  `UnixInodeFileSystem` in `UnixInodeFileSystem.py`; NOT yet active (Wall A).
- Per-mutator maintenance: WALLED on Wall A (cannot state) then Wall B (SMT).
- Trusted uniqueness on `_dir_find_slot`: RETAINED, clearly marked pending,
  pointer to this doc. NOT yet proven.
- os GREEN: 1191 VCs, Verification SUCCESS.
- 7/7 `formal_os_namespace.py` consequences VALID via the standard pipeline.
- byte-diff IDENTICAL (fixed PYTHONHASHSEED); conformance 38/38; determinism
  10/10; doc-coherency green.
- The precise Rocq+Lean lemma to register is `UnixFs.Dir.insert_preserves_unique`
  (§3), and the prerequisite TOOL fix is Wall A (§2).
