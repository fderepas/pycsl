(* LookupFrame.v
 *
 * Validation of UnixFs.Dir.lookup_frame (gap-17, the content round-trip).
 *
 * Models the directory scan _dir_lookup as a Fixpoint over the prefix
 * length i (the slot index 0..16), with an abstract per-slot decode
 * (slot_inode / slot_name) — exactly the shape of UnixDirScan.v and the
 * WhyML axiom.
 *
 * The frame/congruence lemma: dir_lookup depends ONLY on the 16 per-slot
 * decodes (slot_inode / slot_name over k in [0,16)) of the block. Hence
 * any two disk values d0 d1 that agree on those 16 slot decodes yield the
 * same dir_lookup result:
 *
 *   forall d0 d1 blk name,
 *     (forall k, 0 <= k < 16 -> slot_inode d1 blk k = slot_inode d0 blk k) ->
 *     (forall k, 0 <= k < 16 -> slot_name  d1 blk k = slot_name  d0 blk k) ->
 *     dir_lookup d1 blk name = dir_lookup d0 blk name
 *
 * Proved by induction on the prefix length i (for i <= 16): the scan over
 * the first i slots reads only slot j with j < i, so the agreement on
 * slots [0,16) carries it. Then specialize i := 16.
 *
 * Verified under Coq 8.20.1. No Admitted, no Axiom. *)

Require Import Coq.ZArith.ZArith.
Require Import Coq.Bool.Bool.
Require Import Lia.

Open Scope Z_scope.

Module UnixFs.
Module Dir.

(* Abstract per-slot decode: the model leaves slot_inode / slot_name
   uninterpreted (they are the proven name-codec round-trip in the os
   model). The frame property holds for ANY such decode. *)
Section Scan.

Variable disk : Type.            (* the disk byte-array, abstract here *)
Variable name_t : Type.          (* decoded names, abstract here *)
Variable slot_inode : disk -> Z -> Z -> Z.    (* disk -> blk -> k -> inode *)
Variable slot_name  : disk -> Z -> Z -> name_t. (* disk -> blk -> k -> name *)
Variable eqn : name_t -> name_t -> bool.        (* decidable name equality *)

(* The running scan over the first i slots, IDENTICAL to UnixDirScan.v's
   scan: it mirrors _dir_lookup's loop body and keeps the LAST match. *)
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

(* dir_lookup disk blk name := scan disk blk name 16 (-1) — directory
   width is 16, exactly as in UnixDirScan.v. *)
Definition dir_lookup (d : disk) (blk : Z) (name : name_t) : Z :=
  scan d blk name 16 (-1).

(* Prefix frame: for any prefix length i <= 16, if the two disk values
   agree on slot_inode and slot_name for every slot in [0,16), the scan
   over the first i slots agrees. Proved by induction on i: the step peels
   slot j (= i-1 < 16) and uses the agreement at slot j plus the IH. *)
Lemma scan_frame :
  forall (d0 d1 : disk) (blk : Z) (name : name_t) (i : nat) (found : Z),
    (i <= 16)%nat ->
    ( forall k : Z, 0 <= k < 16 -> slot_inode d1 blk k = slot_inode d0 blk k ) ->
    ( forall k : Z, 0 <= k < 16 -> slot_name  d1 blk k = slot_name  d0 blk k ) ->
    scan d1 blk name i found = scan d0 blk name i found.
Proof.
  intros d0 d1 blk name i found Hi Hinode Hname.
  induction i as [| j IH].
  - (* base: empty prefix; scan = found on both. *)
    reflexivity.
  - (* step: peel slot j. Need j < 16 to invoke agreement at slot j. *)
    assert (Hj16 : (j <= 16)%nat) by lia.
    specialize (IH Hj16).
    simpl.
    set (zj := Z.of_nat j) in *.
    (* 0 <= zj < 16 *)
    assert (Hzj_lo : 0 <= zj) by apply Nat2Z.is_nonneg.
    assert (Hzj_hi : zj < 16).
    { unfold zj. assert (Z.of_nat j < Z.of_nat 16) by (apply Nat2Z.inj_lt; lia).
      simpl in *. lia. }
    (* rewrite the slot decodes at j to the d0 values. *)
    rewrite (Hinode zj (conj Hzj_lo Hzj_hi)).
    rewrite (Hname  zj (conj Hzj_lo Hzj_hi)).
    rewrite IH.
    reflexivity.
Qed.

(* The frame on dir_lookup: specialise the prefix frame to i := 16. *)
Lemma dir_lookup_frame :
  forall (d0 d1 : disk) (blk : Z) (name : name_t),
    ( forall k : Z, 0 <= k < 16 -> slot_inode d1 blk k = slot_inode d0 blk k ) ->
    ( forall k : Z, 0 <= k < 16 -> slot_name  d1 blk k = slot_name  d0 blk k ) ->
    dir_lookup d1 blk name = dir_lookup d0 blk name.
Proof.
  intros d0 d1 blk name Hinode Hname.
  unfold dir_lookup.
  apply scan_frame; [ lia | exact Hinode | exact Hname ].
Qed.

End Scan.

(* Closed, fully-qualified statement of the registered axiom
   UnixFs.Dir.lookup_frame, stated OUTSIDE the Section so its statement is
   closed (the abstract disk/name_t/slot_inode/slot_name/eqn are now
   universally quantified, mirroring how UnixDirScan.v exposes its theorems).
   This is the faithful Rocq model of the WhyML registry form. *)
Theorem lookup_frame :
  forall (disk name_t : Type)
         (slot_inode : disk -> Z -> Z -> Z)
         (slot_name  : disk -> Z -> Z -> name_t)
         (eqn : name_t -> name_t -> bool)
         (d0 d1 : disk) (blk : Z) (name : name_t),
    ( forall k : Z, 0 <= k < 16 -> slot_inode d1 blk k = slot_inode d0 blk k ) ->
    ( forall k : Z, 0 <= k < 16 -> slot_name  d1 blk k = slot_name  d0 blk k ) ->
    dir_lookup disk name_t slot_inode slot_name eqn d1 blk name
    = dir_lookup disk name_t slot_inode slot_name eqn d0 blk name.
Proof.
  intros disk name_t slot_inode slot_name eqn d0 d1 blk name Hinode Hname.
  apply dir_lookup_frame; assumption.
Qed.

End Dir.
End UnixFs.

Print Assumptions UnixFs.Dir.lookup_frame.
