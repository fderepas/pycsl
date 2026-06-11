(* Validation of UnixFs.Dir.empty_disk_slots_dead (gap-13, Wall E).
 *
 * The empty-disk establishment axiom for the directory-uniqueness class
 * invariant. The abstract per-slot decode slot_inode (disk, blk, k) reads
 * the 2-byte big-endian inode field of the 32-byte dirent at slot k of block
 * blk. If every byte of the block-5 dirent region is zero, the decoded inode
 * field is 0 for every slot.
 *
 * Modeled FAITHFULLY: slot_inode is defined here as the actual decode --
 * reading the two bytes at the slot offset and combining them big-endian --
 * over an abstract byte-reader `rd : disk -> Z -> Z` (rd d b = byte b of disk
 * d). The hypothesis is that the relevant region reads as 0; the conclusion
 * is that the decode is 0. This MATCHES the registered uninterpreted
 * slot_inode by the relation slot_inode d blk k = decode (rd d) blk k, so the
 * registered axiom (stated over the uninterpreted symbol) is the specialization
 * "region all zero -> slot_inode = 0".
 *
 * Verified under Coq 8.20.1. No Admitted, no Axiom. *)

Require Import Coq.ZArith.ZArith.
Require Import Lia.
Open Scope Z_scope.

Module UnixFs.
Module Dir.
Section Scan.

Variable disk : Type.
(* rd d b : the byte at offset b of disk d (0..255). *)
Variable rd : disk -> Z -> Z.

(* The dirent region of block blk starts at blk*512; slot k occupies bytes
   [blk*512 + 32*k, blk*512 + 32*k + 32). The inode field is the first two
   bytes, big-endian. *)
Definition slot_off (blk k : Z) : Z := blk * 512 + 32 * k.

Definition slot_inode (d : disk) (blk k : Z) : Z :=
  256 * (rd d (slot_off blk k)) + rd d (slot_off blk k + 1).

(* If the two inode-field bytes of every slot k (0<=k<16) of block blk read as
   zero, the decoded inode is zero for every such slot. *)
Theorem empty_disk_slots_dead :
  forall (d : disk) (blk : Z),
    (forall b, blk * 512 <= b < blk * 512 + 512 -> rd d b = 0) ->
    forall k, 0 <= k < 16 -> slot_inode d blk k = 0.
Proof.
  intros d blk Hzero k Hk.
  unfold slot_inode, slot_off.
  rewrite (Hzero (blk * 512 + 32 * k)) by lia.
  rewrite (Hzero (blk * 512 + 32 * k + 1)) by lia.
  lia.
Qed.

Print Assumptions empty_disk_slots_dead.

End Scan.
End Dir.
End UnixFs.
