"""Test 0711 — directory per-slot inode-field byte->decode (Gap-5 keystone, write side).

The forward (value) byte->decode primitive for the directory per-slot inode field.
`slot_inode(disk, blk, k)` is the abstract per-slot decode of the 32-byte dirent at slot
`k` of block `blk` — its inode field is the big-endian uint16 in the first two bytes
(`struct '>H30s'`): `256 * disk[blk*512 + 32*k] + disk[blk*512 + 32*k + 1]`. This is the
SAME 2-byte field `empty_disk_slots_dead` / `block5_decode_frame` already read; this test
exhibits its FORWARD (value) direction.

It is the write-side codec rung the directory write helpers need: a helper that has just
blitted a fresh dirent and proved `disk[off] == b0`, `disk[off+1] == b1` can conclude
`slot_inode(disk, blk, k) == 256*b0 + b1 == inode_num`. UNLIKE the read-side scan fidelity
(`dir_lookup`, which is the inductive closed form of the 16-slot loop and is NOT
SMT-dischargeable from the byte values), this forward value fact IS a finite per-slot
equation, so SMT APPLIES the cited axiom in O(1) under the two byte hypotheses.

TRIGGER DISCIPLINE: the registered axiom is keyed on the BYTE expression
`[disk[blk*512 + 32*k]]`, NOT on `slot_inode` — so it fires only where an explicit slot-byte
term is present (a write helper's post-blit state), never on the ubiquitous abstract
`slot_inode` atoms the uniq / slots_lt32 / scan axiom web triggers on. (Concretizing the
abstract symbol globally instead would E-match-explode — measured; this keeps the decode
read from bytes ONLY when the bytes are there.)

Cross-validated by SlotInodeByteDecode.{v,lean} (theorem slot_inode_byte_decode): unfold the
2-byte decode, rewrite the two byte hypotheses, close by reflexivity. Rocq 8.20.1: Closed
under the global context (only abstract Section Variables, 0 Axiom/Admitted); Lean 4.30.0:
"does not depend on any axioms" (subseteq {propext, Quot.sound}). This file confirms the
axiom APPLIES fast: the empty-body VC is exactly the axiom instantiated under the two byte
hypotheses.
"""

from typing import List


# The byte->decode value fact: if the two inode-field bytes of slot k read as b0, b1, the
# abstract per-slot inode decode is 256*b0 + b1. The cited axiom closes the empty-body VC
# (the postcondition) under the two byte preconditions. `slot_inode` is the SAME abstract
# UnixFs.Dir symbol the os model's directory helpers / scan axioms use.
#@ requires disk[blk * 512 + 32 * k] == b0
#@ requires disk[blk * 512 + 32 * k + 1] == b1
#@ ensures slot_inode(disk, blk, k) == 256 * b0 + b1
#@ proof rocq UnixFs.Dir.slot_inode_byte_decode
#@ proof lean UnixFs.Dir.slot_inode_byte_decode
def slot_inode_value(disk: List[int], blk: int, k: int, b0: int, b1: int) -> None:
    pass


# The END-TO-END write rung: write a fresh inode field (the big-endian uint16 of `inode_num`)
# into slot `k`'s first two bytes, then conclude the abstract per-slot decode equals
# `inode_num`. The two stores establish the byte hypotheses in-body; the cited axiom closes
# the decode. This is the shape the os `_write_dir_entry` / `_write_entry` body proves for
# their `slot_inode(self.dir, blk, slot) == inode_num` write-side ensures.
#@ requires 0 <= inode_num and inode_num < 65536
#@ requires blk >= 0 and blk < 256
#@ requires k >= 0 and k < 16
#@ requires \valid(disk, blk * 512 + 32 * k + 2)
#@ assigns disk[blk * 512 + 32 * k .. blk * 512 + 32 * k + 1]
#@ ensures slot_inode(disk, blk, k) == inode_num
#@ proof rocq UnixFs.Dir.slot_inode_byte_decode
#@ proof lean UnixFs.Dir.slot_inode_byte_decode
def write_inode_field(disk: List[int], blk: int, k: int, inode_num: int) -> None:
    off = blk * 512 + 32 * k
    disk[off] = inode_num // 256
    disk[off + 1] = inode_num % 256
    #@ assert disk[blk * 512 + 32 * k] == inode_num // 256
    #@ assert disk[blk * 512 + 32 * k + 1] == inode_num % 256
    #@ assert (inode_num // 256) * 256 + (inode_num % 256) == inode_num
