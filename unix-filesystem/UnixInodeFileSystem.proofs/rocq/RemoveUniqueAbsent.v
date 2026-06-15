(* unix-filesystem/UnixInodeFileSystem.proofs/rocq/RemoveUniqueAbsent.v
 *
 * Validation of UnixFs.Dir.remove_unique_absent (M4 directory-absence fix).
 *
 * This is the PRODUCER twin of remove_reflects_absent (UnixDirScanAbsent.v):
 * that lemma CONSUMES the absence witness
 *   (forall k <> s, slot_name k = name -> slot_inode k = 0)
 * to conclude dir_lookup < 0. remove_unique_absent PRODUCES exactly that
 * witness from the directory-uniqueness invariant, so the two compose to give
 * the post-removal absence the directory removers (sys_unlink/sys_rmdir/
 * sys_rename) must discharge.
 *
 * Given a pre-removal disk d0 that is `uniq` + `slots_lt32`, where slot s is
 * the live entry being removed, and a post-removal disk d1 that equals d0 off
 * slot s (frame) with slot s now dead: every OTHER slot k whose name equals the
 * removed name (slot_name d0 5 s) is dead on d1.
 *
 * Pure finite first-order reasoning (one application of `uniq` at the pair
 * (k,s)); NO induction, NO scan. This is the O(1) applied fact the removers
 * cite so the explosive `uniq_elim`/`slots_lt32_elim` need not be in their VC
 * context (see 15-0838-remove-unique-absent.md, Part B).
 *
 * Verified under Coq 8.20.1. No Admitted, no Axiom. *)

Require Import Coq.ZArith.ZArith.
Require Import Lia.

Open Scope Z_scope.

Module UnixFs.
Module Dir.

Section Remove.

Variable disk   : Type.
Variable name_t : Type.
Variable slot_inode : disk -> Z -> Z -> Z.
Variable slot_name  : disk -> Z -> Z -> name_t.

(* The abstract directory-uniqueness predicate, at block 5: no two DISTINCT live
   in-range slots share a name. Matches UnixFs.Dir.uniq_elim's unfolded body. *)
Definition uniq (d : disk) : Prop :=
  forall i j : Z,
    0 <= i < 16 -> 0 <= j < 16 ->
    slot_inode d 5 i <> 0 -> slot_inode d 5 i < 32 ->
    slot_inode d 5 j <> 0 -> slot_inode d 5 j < 32 ->
    slot_name d 5 i = slot_name d 5 j -> i = j.

(* Every block-5 slot decodes to an inode < 32. Matches slots_lt32_elim. *)
Definition slots_lt32 (d : disk) : Prop :=
  forall k : Z, 0 <= k < 16 -> slot_inode d 5 k < 32.

Theorem remove_unique_absent :
  forall (d0 d1 : disk) (s : Z),
    uniq d0 ->
    slots_lt32 d0 ->
    0 <= s < 16 ->
    slot_inode d0 5 s <> 0 ->
    slot_inode d1 5 s = 0 ->
    (forall k : Z, 0 <= k < 16 -> k <> s -> slot_inode d1 5 k = slot_inode d0 5 k) ->
    (forall k : Z, 0 <= k < 16 -> k <> s -> slot_name  d1 5 k = slot_name  d0 5 k) ->
    (forall k : Z, 0 <= k < 16 -> k <> s ->
       slot_name d1 5 k = slot_name d0 5 s -> slot_inode d1 5 k = 0).
Proof.
  intros d0 d1 s Huniq Hlt32 Hs Hs0live Hs1dead Hframei Hframen.
  intros k Hk Hks Hname.
  destruct (Z.eq_dec (slot_inode d1 5 k) 0) as [Hz | Hnz].
  - exact Hz.
  - exfalso.
    (* push the frame: slot k is unchanged d0 -> d1. *)
    rewrite (Hframei k Hk Hks) in Hnz.    (* slot_inode d0 5 k <> 0 *)
    rewrite (Hframen k Hk Hks) in Hname.  (* slot_name d0 5 k = slot_name d0 5 s *)
    (* both k and s are live, in range, and < 32, with the same name. *)
    assert (Hk32 : slot_inode d0 5 k < 32) by (apply Hlt32; lia).
    assert (Hs32 : slot_inode d0 5 s < 32) by (apply Hlt32; lia).
    assert (Heq : k = s)
      by (apply (Huniq k s); try lia; assumption).
    lia.
Qed.

End Remove.

End Dir.
End UnixFs.
