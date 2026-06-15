(* unix-filesystem/UnixInodeFileSystem.proofs/rocq/DirLookupFrame.v
 *
 * Validation of UnixFs.Dir.dir_lookup_frame (M4 — unlink reorder).
 *
 * `dir_lookup d blk name` is the bounded 16-slot scan (UnixDirScanAbsent.v):
 * its value is a function of the per-slot decodes slot_inode/slot_name ONLY.
 * Hence two disks d0,d1 that agree on every block-5 slot decode have equal
 * dir_lookup. This lets sys_unlink free the inode blocks (writes confined to
 * block 0, leaving block 5 — and so every slot decode — unchanged) AFTER laying
 * the remove witness, carrying `dir_lookup(self.disk,5,pathname) < 0` across the
 * freeing loop as a scalar invariant (no per-slot terms, so no E-matching storm).
 *
 * Verified under Coq 8.20.1. No Admitted, no Axiom. *)

Require Import Coq.ZArith.ZArith.
Require Import Coq.Bool.Bool.
Require Import Lia.

Open Scope Z_scope.

Module UnixFs.
Module Dir.

Section Frame.

Variable disk : Type.
Variable name_t : Type.
Variable slot_inode : disk -> Z -> Z -> Z.
Variable slot_name  : disk -> Z -> Z -> name_t.
Variable eqn : name_t -> name_t -> bool.

(* The scan, verbatim from UnixDirScanAbsent.v. *)
Fixpoint scan (d : disk) (blk : Z) (name : name_t) (i : nat) (found : Z) : Z :=
  match i with
  | O => found
  | S j =>
      let f := scan d blk name j found in
      let zj := Z.of_nat j in
      if andb (negb (Z.eqb (slot_inode d blk zj) 0))
              (andb (Z.ltb (slot_inode d blk zj) 32)
                    (eqn (slot_name d blk zj) name))
      then slot_inode d blk zj
      else f
  end.

Definition dir_lookup (d : disk) (blk : Z) (name : name_t) : Z :=
  scan d blk name 16 (-1).

(* If d0 and d1 agree on slot_inode/slot_name at every slot j < i (at block 5),
   their i-step scans coincide. Induction on i. *)
Lemma scan_frame :
  forall (d0 d1 : disk) (name : name_t) (i : nat),
    (forall j : Z, 0 <= j < Z.of_nat i ->
       slot_inode d1 5 j = slot_inode d0 5 j /\
       slot_name  d1 5 j = slot_name  d0 5 j) ->
    scan d1 5 name i (-1) = scan d0 5 name i (-1).
Proof.
  intros d0 d1 name i. induction i as [| j IH]; intro Hagree.
  - reflexivity.
  - simpl.
    assert (Hj : 0 <= Z.of_nat j < Z.of_nat (S j)).
    { split; [ apply Nat2Z.is_nonneg | ]. rewrite Nat2Z.inj_succ. lia. }
    destruct (Hagree (Z.of_nat j) Hj) as [Hi Hn].
    rewrite Hi, Hn.
    rewrite IH.
    + reflexivity.
    + intros k Hk. apply Hagree.
      rewrite Nat2Z.inj_succ. lia.
Qed.

Theorem dir_lookup_frame :
  forall (d0 d1 : disk) (name : name_t),
    (forall k : Z, 0 <= k < 16 ->
       slot_inode d1 5 k = slot_inode d0 5 k /\
       slot_name  d1 5 k = slot_name  d0 5 k) ->
    dir_lookup d1 5 name = dir_lookup d0 5 name.
Proof.
  intros d0 d1 name Hframe. unfold dir_lookup.
  apply scan_frame.
  intros j Hj. apply Hframe. replace (Z.of_nat 16) with 16 in Hj by reflexivity. lia.
Qed.

End Frame.

End Dir.
End UnixFs.
