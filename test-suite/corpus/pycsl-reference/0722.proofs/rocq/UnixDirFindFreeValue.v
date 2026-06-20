(* Value theorem for _dir_find_free: the FREE-SLOT-INDEX dual of
   dir_find_slot_result (UnixDirFindSlotValue.v). _dir_find_free scans the 16
   directory slots and returns the INDEX (0..15) of the LAST slot whose inode
   field is 0 (a FREE slot), or -1 if the block is full. Unlike _dir_find_slot
   it reads ONLY slot_inode (NO name decode), and the match condition is
   `slot_inode = 0` (free) rather than `slot_inode <> 0 /\ slot_name = name`
   (live). This cross-validates the dir_find_free_result marker family: the
   read-side fidelity that the returned slot index has slot_inode = 0.

   Same shape and the SAME abstract per-slot decode (slot_inode) as
   UnixDirFindSlot.v, over a free-slot predicate. The marker fires ONLY at the
   atoms _dir_find_free's body asserts (loop-carry prefix + loop-exit close),
   NEVER on a bare slot_inode term — the once-firing discipline of its twin.
   Verified under Coq 8.20.1. No Admitted, no Axiom (Section Variables only). *)
Require Import Coq.ZArith.ZArith.
Require Import Coq.Bool.Bool.
Require Import Lia.
Open Scope Z_scope.

Module UnixFs.
Module Dir.
Section FindFree.
Variable disk : Type.
Variable slot_inode : disk -> Z -> Z -> Z.

(* A slot k is FREE in block `blk` iff its inode field decodes to 0. This is
   exactly _dir_find_free's loop guard `if inode_num == 0`. *)
Definition is_free (d : disk) (blk : Z) (k : Z) : Prop :=
  slot_inode d blk k = 0.

(* The running FREE-SLOT-INDEX scan over the first i slots, mirroring
   _dir_find_free's loop body `if inode_num == 0: found = i`. It keeps the LAST
   free INDEX (recurse first, then test slot j); when slot j is free the
   carried `found` becomes the INDEX zj. *)
Fixpoint ffscan (d : disk) (blk : Z) (i : nat) (found : Z) : Z :=
  match i with
  | O => found
  | S j =>
      let f := ffscan d blk j found in
      let zj := Z.of_nat j in
      if Z.eqb (slot_inode d blk zj) 0
      then zj
      else f
  end.

(* The carry invariant proved at every prefix length i: if the running index
   `found` started >= 0 then it is a free slot, AND the result is either the
   start value or a free in-range index. *)
Lemma ffscan_result_free : forall (d : disk) (blk : Z) (i : nat) (start : Z),
  let r := ffscan d blk i start in
  ( (0 <= r < Z.of_nat i /\ is_free d blk r) \/ r = start ).
Proof.
  intros d blk i start. induction i as [| j IH].
  - (* base: ffscan = start. *)
    simpl. right. reflexivity.
  - (* step: peel slot j. *)
    simpl.
    set (zj := Z.of_nat j) in *.
    remember (Z.eqb (slot_inode d blk zj) 0) as guard eqn:Hguard.
    destruct guard.
    + (* guard true: result = index zj, a free slot. *)
      symmetry in Hguard. apply Z.eqb_eq in Hguard.
      left. split.
      * split. apply Nat2Z.is_nonneg. lia.
      * unfold is_free. exact Hguard.
    + (* guard false: result = ffscan over j; classify via IH. *)
      destruct IH as [ [Hrng Hf] | Heq ].
      * left. split; [ lia | exact Hf ].
      * right. exact Heq.
Qed.

(* dir_find_free d blk := ffscan d blk 16 (-1). *)
Definition dir_find_free (d : disk) (blk : Z) : Z :=
  ffscan d blk 16 (-1).

(* The MARKER: dir_find_free_result d blk r holds iff r is exactly the bounded
   16-slot free-index scan result. DEFINITIONAL (zero TCB). *)
Definition dir_find_free_result (d : disk) (blk : Z) (r : Z) : Prop :=
  ffscan d blk 16 (-1) = r.

(* dir_find_free_result_intro (DEFINITIONAL, zero trust). *)
Theorem dir_find_free_result_intro :
  forall (d : disk) (blk : Z) (r : Z),
    ffscan d blk 16 (-1) = r -> dir_find_free_result d blk r.
Proof. intros. unfold dir_find_free_result. exact H. Qed.

(* dir_find_free_result_value (cross-validated VALUE lemma — the load-bearing
   free-slot fidelity): when r >= 0, slot r has slot_inode = 0. This is exactly
   _dir_find_free's fidelity ensures `\result >= 0 ==> slot_inode = 0`. *)
Theorem dir_find_free_result_value :
  forall (d : disk) (blk : Z) (r : Z),
    dir_find_free_result d blk r ->
    r >= 0 ->
    slot_inode d blk r = 0.
Proof.
  intros d blk r Hmk Hpos. unfold dir_find_free_result in Hmk.
  pose proof (ffscan_result_free d blk 16 (-1)) as Hinv.
  cbv zeta in Hinv. rewrite Hmk in Hinv.
  destruct Hinv as [ [Hrng Hf] | Heq ].
  - unfold is_free in Hf. exact Hf.
  - (* r = -1 here (start = -1), contradicts r >= 0 *)
    lia.
Qed.

(* dir_find_free_result_range (DEFINITIONAL, zero trust): r in [-1, 16). *)
Theorem dir_find_free_result_range :
  forall (d : disk) (blk : Z) (r : Z),
    dir_find_free_result d blk r -> -1 <= r < 16.
Proof.
  intros d blk r Hmk. unfold dir_find_free_result in Hmk.
  pose proof (ffscan_result_free d blk 16 (-1)) as Hinv.
  cbv zeta in Hinv. rewrite Hmk in Hinv.
  replace (Z.of_nat 16) with 16 in Hinv by reflexivity.
  destruct Hinv as [ [Hrng _] | Heq ].
  - lia.
  - lia.
Qed.

End FindFree.
End Dir.
End UnixFs.

(* ===== Prefix-marker form: a NON-inductive loop-carry rung ===== *)
Module Prefix.
Section P.
Variable disk : Type.
Variable slot_inode : disk -> Z -> Z -> Z.

(* dir_find_free_prefix d blk i r : "r is the free-index scan over the first i
   slots" -- the loop-carry marker. i is the loop counter; r is `found`. *)
Definition dir_find_free_prefix (d:disk) (blk:Z) (i:Z) (r:Z) : Prop :=
  (0 <= i <= 16) /\
  UnixFs.Dir.ffscan disk slot_inode d blk (Z.to_nat i) (-1) = r.

(* Base: prefix 0 has result -1 (the loop init). *)
Theorem dir_find_free_prefix_base :
  forall d blk, dir_find_free_prefix d blk 0 (-1).
Proof. intros. unfold dir_find_free_prefix. simpl. split; [lia | reflexivity]. Qed.

(* Step: the loop-body update. From prefix i with result r, peeling slot i
   (zi = i) gives prefix (i+1) with the body's `if` update. This is EXACTLY
   the loop body `if inode_num == 0: found = i`. *)
Theorem dir_find_free_prefix_step :
  forall d blk i r,
    0 <= i < 16 ->
    dir_find_free_prefix d blk i r ->
    ( slot_inode d blk i = 0
        -> dir_find_free_prefix d blk (i+1) i ) /\
    ( slot_inode d blk i <> 0
        -> dir_find_free_prefix d blk (i+1) r ).
Proof.
  intros d blk i r Hi [Hib Hpre].
  assert (Hni : Z.to_nat (i+1) = S (Z.to_nat i)).
  { rewrite Z2Nat.inj_add by lia. simpl. lia. }
  assert (Hzi : Z.of_nat (Z.to_nat i) = i) by (rewrite Z2Nat.id; lia).
  split.
  - intros Hfree. unfold dir_find_free_prefix. split; [lia|].
    rewrite Hni. simpl. rewrite Hpre. rewrite Hzi.
    assert (Hg: Z.eqb (slot_inode d blk i) 0 = true).
    { apply Z.eqb_eq. exact Hfree. }
    rewrite Hg. reflexivity.
  - intros Hne. unfold dir_find_free_prefix. split; [lia|].
    rewrite Hni. simpl. rewrite Hpre. rewrite Hzi.
    assert (Hg: Z.eqb (slot_inode d blk i) 0 = false).
    { apply Z.eqb_neq. exact Hne. }
    rewrite Hg. reflexivity.
Qed.

(* Closeout: prefix 16 is the full dir_find_free value, folded to the result
   marker. *)
Theorem dir_find_free_prefix_close :
  forall d blk r,
    dir_find_free_prefix d blk 16 r ->
    UnixFs.Dir.dir_find_free_result disk slot_inode d blk r.
Proof.
  intros d blk r [_ H]. unfold UnixFs.Dir.dir_find_free_result.
  simpl in H. exact H.
Qed.

End P.
End Prefix.
