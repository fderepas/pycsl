(* unix-filesystem/UnixInodeFileSystem.proofs/rocq/InsertPreservesUnique.v
 *
 * Validation of UnixFs.Dir.insert_preserves_unique (gap-12).
 *
 * The INSERT companion of remove_reflects_absent (UnixDirScanAbsent.v). It is
 * the maintenance lemma for the directory-uniqueness CLASS INVARIANT: starting
 * from a disk whose 16 live slots have no duplicate live name, if one slot s is
 * made live with a name nm that was NOT already among the live names (the EEXIST
 * guard) and every OTHER slot is byte-for-byte unchanged (the _write_entry
 * slot-locality frame), then the resulting disk still has no duplicate live name.
 *
 * Faithful (not over-strong): asserts only the structural no-duplicate-created
 * fact; says nothing about the decode-vs-bytes correspondence (that stays in the
 * trusted dirscan-fidelity decode ensures). A finite 4-way case split, no
 * induction, discharged by lia and rewriting under the frame.
 *
 * Verified under Coq 8.20.1. No Admitted, no Axiom.
 * Print Assumptions = Closed under the global context (only the four abstract
 * Section Variables disk / name_t / slot_inode / slot_name). *)

Require Import Coq.ZArith.ZArith.
Require Import Lia.

Open Scope Z_scope.

Module UnixFs.
Module Dir.

Section Scan.

Variable disk : Type.
Variable name_t : Type.
Variable slot_inode : disk -> Z -> Z -> Z.
Variable slot_name  : disk -> Z -> Z -> name_t.

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
  destruct (Z.eq_dec i s) as [Eis|Nis]; destruct (Z.eq_dec j s) as [Ejs|Njs].
  - lia.                                   (* i=s, j=s => i=j *)
  - (* i=s (name nm), j<>s: j live on d0, name(j)=nm, contradicts Hfresh. *)
    exfalso. subst i.
    destruct (Hframe j Hj Njs) as [Hij Hnj].
    apply (Hfresh j Hj).
    + rewrite <- Hij. exact Hjl.
    + rewrite <- Hij. exact Hjb.
    + rewrite <- Hnj. rewrite <- Hnameq. exact Hsnm.
  - (* symmetric: j=s, i<>s. *)
    exfalso. subst j.
    destruct (Hframe i Hi Nis) as [Hii Hni].
    apply (Hfresh i Hi).
    + rewrite <- Hii. exact Hil.
    + rewrite <- Hii. exact Hib.
    + rewrite <- Hni. rewrite Hnameq. exact Hsnm.
  - (* i<>s, j<>s: both decodes equal d0's, so Hinv0 applies. *)
    destruct (Hframe i Hi Nis) as [Hii Hni].
    destruct (Hframe j Hj Njs) as [Hij Hnj].
    apply (Hinv0 i j Hi Hj).
    + rewrite <- Hii. exact Hil.
    + rewrite <- Hii. exact Hib.
    + rewrite <- Hij. exact Hjl.
    + rewrite <- Hij. exact Hjb.
    + rewrite <- Hni, <- Hnj. exact Hnameq.
Qed.

Print Assumptions insert_preserves_unique.

End Scan.

End Dir.
End UnixFs.
