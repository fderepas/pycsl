(* Validation of UnixFs.Dir.block5_decode_frame (gap-13, Wall M).
 *
 * The decode-locality lemma for the directory-uniqueness class invariant. The
 * abstract per-slot decode slot_inode/slot_name (disk, 5, k) reads ONLY the
 * 32-byte dirent of slot k inside block 5's region [2560, 3072): the inode
 * field is the 2 bytes at [off, off+2), the name is the 30 bytes [off+2,off+32),
 * where off = 2560 + 32*k. Hence two disks agreeing on every byte of
 * [2560,3072) have identical block-5 decode at every slot k in [0,16).
 *
 * Modeled FAITHFULLY: rd is the abstract byte reader; inode_decode combines the
 * two bytes big-endian; name_decode is an arbitrary function of the 30 name
 * bytes (passed explicitly). The proof rewrites each read under the byte
 * agreement -- no functional extensionality, no induction. Same trust class as
 * empty_disk_slots_dead.
 *
 * Verified under Coq 8.20.1. No Admitted, no Axiom (only Section Variables). *)

Require Import Coq.ZArith.ZArith.
Require Import Lia.
Open Scope Z_scope.

Module UnixFs.
Module Dir.
Section Scan.

Variable byte_disk : Type.
Variable rd : byte_disk -> Z -> Z.
Variable name_t : Type.
(* name_decode takes the 30 name bytes explicitly (b2..b31). *)
Variable name_decode :
  Z->Z->Z->Z->Z->Z->Z->Z->Z->Z->Z->Z->Z->Z->Z->
  Z->Z->Z->Z->Z->Z->Z->Z->Z->Z->Z->Z->Z->Z->Z-> name_t.

Definition slot_off5 (k : Z) : Z := 2560 + 32 * k.

Definition slot_inode (d : byte_disk) (k : Z) : Z :=
  256 * (rd d (slot_off5 k)) + rd d (slot_off5 k + 1).

Definition slot_name (d : byte_disk) (k : Z) : name_t :=
  let o := slot_off5 k in
  name_decode (rd d (o+2)) (rd d (o+3)) (rd d (o+4)) (rd d (o+5)) (rd d (o+6))
              (rd d (o+7)) (rd d (o+8)) (rd d (o+9)) (rd d (o+10)) (rd d (o+11))
              (rd d (o+12))(rd d (o+13))(rd d (o+14))(rd d (o+15))(rd d (o+16))
              (rd d (o+17))(rd d (o+18))(rd d (o+19))(rd d (o+20))(rd d (o+21))
              (rd d (o+22))(rd d (o+23))(rd d (o+24))(rd d (o+25))(rd d (o+26))
              (rd d (o+27))(rd d (o+28))(rd d (o+29))(rd d (o+30))(rd d (o+31)).

Theorem block5_decode_frame :
  forall (d0 d1 : byte_disk),
    (forall b, 2560 <= b < 3072 -> rd d0 b = rd d1 b) ->
    forall k, 0 <= k < 16 ->
      slot_inode d1 k = slot_inode d0 k /\
      slot_name  d1 k = slot_name  d0 k.
Proof.
  intros d0 d1 Hagree k Hk.
  assert (Hwin : forall i, 0 <= i < 32 -> rd d0 (slot_off5 k + i) = rd d1 (slot_off5 k + i)).
  { intros i Hi. apply Hagree. unfold slot_off5. lia. }
  split.
  - unfold slot_inode, slot_off5.
    rewrite (Hagree (2560 + 32 * k)) by lia.
    rewrite (Hagree (2560 + 32 * k + 1)) by lia.
    reflexivity.
  - unfold slot_name.
    assert (E : forall i, 0 <= i < 32 -> rd d1 (slot_off5 k + i) = rd d0 (slot_off5 k + i)).
    { intros i Hi. symmetry. apply Hwin. exact Hi. }
    rewrite (E 2 ltac:(lia)),  (E 3 ltac:(lia)),  (E 4 ltac:(lia)),  (E 5 ltac:(lia)),
            (E 6 ltac:(lia)),  (E 7 ltac:(lia)),  (E 8 ltac:(lia)),  (E 9 ltac:(lia)),
            (E 10 ltac:(lia)), (E 11 ltac:(lia)), (E 12 ltac:(lia)), (E 13 ltac:(lia)),
            (E 14 ltac:(lia)), (E 15 ltac:(lia)), (E 16 ltac:(lia)), (E 17 ltac:(lia)),
            (E 18 ltac:(lia)), (E 19 ltac:(lia)), (E 20 ltac:(lia)), (E 21 ltac:(lia)),
            (E 22 ltac:(lia)), (E 23 ltac:(lia)), (E 24 ltac:(lia)), (E 25 ltac:(lia)),
            (E 26 ltac:(lia)), (E 27 ltac:(lia)), (E 28 ltac:(lia)), (E 29 ltac:(lia)),
            (E 30 ltac:(lia)), (E 31 ltac:(lia)).
    reflexivity.
Qed.

Print Assumptions block5_decode_frame.

End Scan.
End Dir.
End UnixFs.
