-- unix-filesystem/UnixInodeFileSystem.proofs/lean/RemoveUniqueAbsent.lean
--
-- Lean 4 cross-validation twin of UnixFs.Dir.remove_unique_absent (M4 fix).
--
-- PRODUCER twin of remove_reflects_absent (UnixDirScanAbsent.lean): produces the
-- post-removal absence witness (every other same-named slot is dead) from the
-- directory-uniqueness invariant `uniq` + the `slots_lt32` bound + the removal
-- frame. The O(1) applied fact the directory removers cite so the explosive
-- uniq_elim/slots_lt32_elim stay out of their VC context.
--
-- Pure finite first-order reasoning (one use of `uniq` at the pair (k,s)); no
-- induction. Verified under Lean 4.30.0 (core only, no Mathlib).

namespace UnixFs.Dir

variable {Disk : Type} {NameT : Type}
variable (slotInode : Disk → Int → Int → Int)
variable (slotName  : Disk → Int → Int → NameT)

-- Directory-uniqueness at block 5: no two distinct live in-range slots share a
-- name. Matches UnixFs.Dir.uniq_elim's unfolded body.
def uniq (d : Disk) : Prop :=
  ∀ i j : Int, 0 ≤ i → i < 16 → 0 ≤ j → j < 16 →
    slotInode d 5 i ≠ 0 → slotInode d 5 i < 32 →
    slotInode d 5 j ≠ 0 → slotInode d 5 j < 32 →
    slotName d 5 i = slotName d 5 j → i = j

-- Every block-5 slot decodes to an inode < 32. Matches slots_lt32_elim.
def slots_lt32 (d : Disk) : Prop :=
  ∀ k : Int, 0 ≤ k → k < 16 → slotInode d 5 k < 32

theorem remove_unique_absent
    (d0 d1 : Disk) (s : Int)
    (hUniq : uniq slotInode slotName d0)
    (hLt32 : slots_lt32 slotInode d0)
    (hs0 : 0 ≤ s) (hs1 : s < 16)
    (hs0live : slotInode d0 5 s ≠ 0)
    (hs1dead : slotInode d1 5 s = 0)
    (hframei : ∀ k : Int, 0 ≤ k → k < 16 → k ≠ s → slotInode d1 5 k = slotInode d0 5 k)
    (hframen : ∀ k : Int, 0 ≤ k → k < 16 → k ≠ s → slotName d1 5 k = slotName d0 5 k) :
    ∀ k : Int, 0 ≤ k → k < 16 → k ≠ s →
      slotName d1 5 k = slotName d0 5 s → slotInode d1 5 k = 0 := by
  intro k hk0 hk1 hks hname
  -- push the frame: slot k is unchanged d0 -> d1.
  rw [hframei k hk0 hk1 hks]
  rw [hframen k hk0 hk1 hks] at hname
  by_cases h : slotInode d0 5 k = 0
  · exact h
  · exfalso
    have hk32 : slotInode d0 5 k < 32 := hLt32 k hk0 hk1
    have hs32 : slotInode d0 5 s < 32 := hLt32 s hs0 hs1
    have heq : k = s := hUniq k s hk0 hk1 hs0 hs1 h hk32 hs0live hs32 hname
    exact hks heq

end UnixFs.Dir
