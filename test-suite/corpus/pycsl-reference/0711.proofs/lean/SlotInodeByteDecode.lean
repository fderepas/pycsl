/- Validation of UnixFs.Dir.slot_inode_byte_decode (Gap-5 keystone, write side)
   -- Lean 4 mirror of ../rocq/SlotInodeByteDecode.v.

   The WRITE-DIRECTION byte->decode fact for the directory per-slot inode field.
   slot_inode is the faithful 2-byte big-endian decode over an abstract byte-
   reader rd (identical to EmptyDiskSlotsDead.lean). If the two inode-field
   bytes of slot k read as b0, b1, the decode is 256*b0 + b1.

   Verified under Lean 4.30.0 (core only, no Mathlib). No sorry. -/

namespace UnixFs
namespace Dir
section Scan

variable {disk : Type}

def slotOff (blk k : Int) : Int := blk * 512 + 32 * k

def slotInode (rd : disk → Int → Int) (d : disk) (blk k : Int) : Int :=
  256 * (rd d (slotOff blk k)) + rd d (slotOff blk k + 1)

theorem slot_inode_byte_decode
    (rd : disk → Int → Int) (d : disk) (blk k b0 b1 : Int)
    (H0 : rd d (slotOff blk k) = b0)
    (H1 : rd d (slotOff blk k + 1) = b1) :
    slotInode rd d blk k = 256 * b0 + b1 := by
  unfold slotInode
  rw [H0, H1]

#print axioms slot_inode_byte_decode

end Scan
end Dir
end UnixFs
