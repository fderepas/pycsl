/- Validation of UnixFs.Dir.empty_disk_slots_dead (gap-13, Wall E) -- Lean 4
   mirror of ../rocq/EmptyDiskSlotsDead.v.

   The empty-disk establishment axiom: the abstract per-slot decode of an
   all-zero block-5 dirent region is 0 at every slot. slot_inode is defined as
   the faithful 2-byte big-endian decode over an abstract byte-reader rd; the
   hypothesis is region-all-zero, the conclusion is slot_inode = 0.

   Verified under Lean 4.30.0 (core only, no Mathlib). No sorry. -/

namespace UnixFs
namespace Dir
section Scan

variable {disk : Type}

def slotOff (blk k : Int) : Int := blk * 512 + 32 * k

def slotInode (rd : disk → Int → Int) (d : disk) (blk k : Int) : Int :=
  256 * (rd d (slotOff blk k)) + rd d (slotOff blk k + 1)

theorem empty_disk_slots_dead
    (rd : disk → Int → Int) (d : disk) (blk : Int)
    (Hzero : ∀ b, blk * 512 ≤ b → b < blk * 512 + 512 → rd d b = 0) :
    ∀ k, 0 ≤ k → k < 16 → slotInode rd d blk k = 0 := by
  intro k Hk0 Hk16
  have h1 : rd d (slotOff blk k) = 0 := by
    apply Hzero <;> unfold slotOff <;> omega
  have h2 : rd d (slotOff blk k + 1) = 0 := by
    apply Hzero <;> unfold slotOff <;> omega
  unfold slotInode
  rw [h1, h2]
  omega

#print axioms empty_disk_slots_dead

end Scan
end Dir
end UnixFs
