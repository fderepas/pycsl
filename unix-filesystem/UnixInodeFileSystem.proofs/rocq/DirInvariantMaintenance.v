(* unix-filesystem/UnixInodeFileSystem.proofs/rocq/DirInvariantMaintenance.v
 *
 * Validation of the FOLDED directory-invariant maintenance facts (M4 fix).
 *
 * These replace the definitional uniq_intro/uniq_elim/slots_lt32_intro/
 * slots_lt32_elim in the os module. Those elims unfold the invariant into a
 * nested `forall i j` / `forall k` whose E-matching explodes in the term-rich
 * directory removers (15-0838-remove-unique-absent.md §2). Each fact below
 * states the establishment / frame / zero / insert step over the FOLDED
 * predicates `uniq` / `slots_lt32` as OPAQUE atoms — all the unfolding is
 * discharged HERE, so the os never has the explosive nested quantifiers in any
 * VC. A writer APPLIES the matching fact in O(1); the removers carry none of the
 * elims.
 *
 * `uniq` / `slots_lt32` are at block 5 (the directory block), matching the os
 * call sites. Pure finite first-order reasoning; no induction.
 *
 * Verified under Coq 8.20.1. No Admitted, no Axiom. *)

Require Import Coq.ZArith.ZArith.
Require Import Lia.

Open Scope Z_scope.

Module UnixFs.
Module Dir.

Section Maintenance.

Variable disk   : Type.
Variable name_t : Type.
Variable slot_inode : disk -> Z -> Z -> Z.
Variable slot_name  : disk -> Z -> Z -> name_t.

(* No two DISTINCT live in-range slots share a name (at block 5). *)
Definition uniq (d : disk) : Prop :=
  forall i j : Z,
    0 <= i < 16 -> 0 <= j < 16 ->
    slot_inode d 5 i <> 0 -> slot_inode d 5 i < 32 ->
    slot_inode d 5 j <> 0 -> slot_inode d 5 j < 32 ->
    slot_name d 5 i = slot_name d 5 j -> i = j.

(* Every block-5 slot decodes to an inode < 32. *)
Definition slots_lt32 (d : disk) : Prop :=
  forall k : Z, 0 <= k < 16 -> slot_inode d 5 k < 32.

(* ---- ESTABLISH (constructor / empty disk) ---- *)

(* All slots dead => uniq vacuously (the live-pair antecedent is false). *)
Theorem establish_uniq :
  forall d : disk,
    (forall k : Z, 0 <= k < 16 -> slot_inode d 5 k = 0) ->
    uniq d.
Proof.
  intros d Hdead i j Hi Hj Hilive _ _ _ _.
  exfalso. apply Hilive. apply Hdead. exact Hi.
Qed.

Theorem establish_slots_lt32 :
  forall d : disk,
    (forall k : Z, 0 <= k < 16 -> slot_inode d 5 k = 0) ->
    slots_lt32 d.
Proof.
  intros d Hdead k Hk. rewrite (Hdead k Hk). lia.
Qed.

(* ---- FRAME (non-block-5 writer: block-5 decode unchanged) ---- *)

Theorem frame_preserves_uniq :
  forall d0 d1 : disk,
    uniq d0 ->
    (forall k : Z, 0 <= k < 16 ->
       slot_inode d1 5 k = slot_inode d0 5 k /\
       slot_name  d1 5 k = slot_name  d0 5 k) ->
    uniq d1.
Proof.
  intros d0 d1 H0 Hfr i j Hi Hj Hil Hilt Hjl Hjlt Hnm.
  destruct (Hfr i Hi) as [Hii Hin].
  destruct (Hfr j Hj) as [Hji Hjn].
  apply (H0 i j Hi Hj).
  - rewrite <- Hii; exact Hil.
  - rewrite <- Hii; exact Hilt.
  - rewrite <- Hji; exact Hjl.
  - rewrite <- Hji; exact Hjlt.
  - rewrite <- Hin, <- Hjn; exact Hnm.
Qed.

Theorem frame_preserves_slots_lt32 :
  forall d0 d1 : disk,
    slots_lt32 d0 ->
    (forall k : Z, 0 <= k < 16 -> slot_inode d1 5 k = slot_inode d0 5 k) ->
    slots_lt32 d1.
Proof.
  intros d0 d1 H0 Hfr k Hk. rewrite (Hfr k Hk). apply H0. exact Hk.
Qed.

(* ---- ZERO (remover: slot s cleared, rest framed) ---- *)

Theorem zero_preserves_uniq :
  forall (d0 d1 : disk) (s : Z),
    uniq d0 ->
    slot_inode d1 5 s = 0 ->
    (forall k : Z, 0 <= k < 16 -> k <> s ->
       slot_inode d1 5 k = slot_inode d0 5 k /\
       slot_name  d1 5 k = slot_name  d0 5 k) ->
    uniq d1.
Proof.
  intros d0 d1 s H0 Hs0 Hfr i j Hi Hj Hil Hilt Hjl Hjlt Hnm.
  (* live slots on d1 cannot be s (s is dead), so the frame applies to both. *)
  assert (His : i <> s) by (intro; subst; rewrite Hs0 in Hil; apply Hil; reflexivity).
  assert (Hjs : j <> s) by (intro; subst; rewrite Hs0 in Hjl; apply Hjl; reflexivity).
  destruct (Hfr i Hi His) as [Hii Hin].
  destruct (Hfr j Hj Hjs) as [Hji Hjn].
  apply (H0 i j Hi Hj).
  - rewrite <- Hii; exact Hil.
  - rewrite <- Hii; exact Hilt.
  - rewrite <- Hji; exact Hjl.
  - rewrite <- Hji; exact Hjlt.
  - rewrite <- Hin, <- Hjn; exact Hnm.
Qed.

Theorem zero_preserves_slots_lt32 :
  forall (d0 d1 : disk) (s : Z),
    slots_lt32 d0 ->
    slot_inode d1 5 s = 0 ->
    (forall k : Z, 0 <= k < 16 -> k <> s ->
       slot_inode d1 5 k = slot_inode d0 5 k) ->
    slots_lt32 d1.
Proof.
  intros d0 d1 s H0 Hs0 Hfr k Hk.
  destruct (Z.eq_dec k s) as [He | Hne].
  - subst k. rewrite Hs0. lia.
  - rewrite (Hfr k Hk Hne). apply H0. exact Hk.
Qed.

(* ---- INSERT (writer: slot s becomes live with a fresh name, rest framed) ---- *)

(* nm-free form: the inserted name is `slot_name d1 5 s` itself, so the fact is
   triggerable on [slot_name d1 5 s, uniq d0] (binds d0,d1,s; no untriggerable
   name binder). The freshness hypothesis says no live slot of d0 already carries
   the name that slot s gets on d1. *)
Theorem insert_preserves_uniq_folded :
  forall (d0 d1 : disk) (s : Z),
    uniq d0 ->
    0 <= s < 16 ->
    (forall k : Z, 0 <= k < 16 ->
       slot_inode d0 5 k <> 0 -> slot_inode d0 5 k < 32 ->
       slot_name d0 5 k <> slot_name d1 5 s) ->
    (forall k : Z, 0 <= k < 16 -> k <> s ->
       slot_inode d1 5 k = slot_inode d0 5 k /\
       slot_name  d1 5 k = slot_name  d0 5 k) ->
    (slot_inode d1 5 s <> 0 -> slot_inode d1 5 s < 32) ->
    uniq d1.
Proof.
  intros d0 d1 s H0 Hs Hfresh Hfr Hslt i j Hi Hj Hil Hilt Hjl Hjlt Hnm.
  (* Case on whether i or j is the inserted slot s. *)
  destruct (Z.eq_dec i s) as [His | His];
  destruct (Z.eq_dec j s) as [Hjs | Hjs].
  - subst; reflexivity.
  - (* i = s, j <> s: then slot j has name nm and is live on d0 -> contradicts fresh. *)
    exfalso. subst i.
    destruct (Hfr j Hj Hjs) as [Hji Hjn].
    assert (Hjnm : slot_name d0 5 j = slot_name d1 5 s) by congruence.
    apply (Hfresh j Hj).
    + rewrite <- Hji; exact Hjl.
    + rewrite <- Hji; exact Hjlt.
    + exact Hjnm.
  - (* j = s, i <> s: symmetric. *)
    exfalso. subst j.
    destruct (Hfr i Hi His) as [Hii Hin].
    assert (Hinm : slot_name d0 5 i = slot_name d1 5 s) by congruence.
    apply (Hfresh i Hi).
    + rewrite <- Hii; exact Hil.
    + rewrite <- Hii; exact Hilt.
    + exact Hinm.
  - (* both <> s: frame both to d0, apply uniq d0. *)
    destruct (Hfr i Hi His) as [Hii Hin].
    destruct (Hfr j Hj Hjs) as [Hji Hjn].
    apply (H0 i j Hi Hj).
    + rewrite <- Hii; exact Hil.
    + rewrite <- Hii; exact Hilt.
    + rewrite <- Hji; exact Hjl.
    + rewrite <- Hji; exact Hjlt.
    + rewrite <- Hin, <- Hjn; exact Hnm.
Qed.

Theorem insert_preserves_slots_lt32 :
  forall (d0 d1 : disk) (s : Z),
    slots_lt32 d0 ->
    0 <= s < 16 ->
    slot_inode d1 5 s < 32 ->
    (forall k : Z, 0 <= k < 16 -> k <> s ->
       slot_inode d1 5 k = slot_inode d0 5 k) ->
    slots_lt32 d1.
Proof.
  intros d0 d1 s H0 Hs Hslt Hfr k Hk.
  destruct (Z.eq_dec k s) as [He | Hne].
  - subst k. exact Hslt.
  - rewrite (Hfr k Hk Hne). apply H0. exact Hk.
Qed.

End Maintenance.

End Dir.
End UnixFs.
