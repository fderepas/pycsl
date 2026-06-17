(* Validation of UnixFs.Dir.slot_inode_byte_decode (Gap-5 keystone, write side).
 *
 * The WRITE-DIRECTION byte->decode fact for the directory per-slot inode field.
 * slot_inode (disk, blk, k) reads the 2-byte big-endian inode field of the
 * 32-byte dirent at slot k of block blk: 256*rd(off) + rd(off+1), off =
 * blk*512 + 32*k. This axiom states exactly that equation against the two
 * concrete on-disk bytes, so a write helper that has just blitted those two
 * bytes (and proved disk[off]=b0, disk[off+1]=b1) can conclude
 * slot_inode disk blk k = 256*b0 + b1 = inode_num.
 *
 * This is the read of the SAME 2-byte field that empty_disk_slots_dead and
 * block5_decode_frame already use (EmptyDiskSlotsDead.v line 37-38); it is the
 * forward (value) direction those used only at zero / for the frame. Faithful:
 * a property of _unpack_uint16_be of the dirent inode field. Reuses the SAME
 * abstract slot_inode symbol (no new registry function).
 *
 * Verified under Coq 8.20.1. No Admitted, no Axiom (only abstract Section
 * Variables). *)

Require Import Coq.ZArith.ZArith.
Require Import Lia.
Open Scope Z_scope.

Module UnixFs.
Module Dir.
Section Scan.

Variable disk : Type.
(* rd d b : the byte at offset b of disk d. *)
Variable rd : disk -> Z -> Z.

Definition slot_off (blk k : Z) : Z := blk * 512 + 32 * k.

(* The faithful decode -- identical to EmptyDiskSlotsDead.v. *)
Definition slot_inode (d : disk) (blk k : Z) : Z :=
  256 * (rd d (slot_off blk k)) + rd d (slot_off blk k + 1).

(* WRITE-DIRECTION: if the two inode-field bytes of slot k read as b0, b1,
   then the decode is 256*b0 + b1. This is the registered axiom's content,
   stated over the uninterpreted slot_inode by the relation
   slot_inode d blk k = decode (rd d) blk k. *)
Theorem slot_inode_byte_decode :
  forall (d : disk) (blk k b0 b1 : Z),
    rd d (slot_off blk k) = b0 ->
    rd d (slot_off blk k + 1) = b1 ->
    slot_inode d blk k = 256 * b0 + b1.
Proof.
  intros d blk k b0 b1 H0 H1.
  unfold slot_inode.
  rewrite H0, H1.
  reflexivity.
Qed.

Print Assumptions slot_inode_byte_decode.

End Scan.
End Dir.
End UnixFs.
