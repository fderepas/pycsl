-- unix-filesystem/UnixInodeFileSystem.proofs/lean/DirInvariantMaintenance.lean
--
-- Lean 4 cross-validation twins of the FOLDED directory-invariant maintenance
-- facts (M4 fix). These replace uniq_intro/uniq_elim/slots_lt32_intro/
-- slots_lt32_elim in the os module: each states the establishment / frame /
-- zero / insert step over the FOLDED `uniq`/`slots_lt32` atoms, discharging the
-- nested-quantifier unfolding HERE so the os never carries the explosive elims
-- (15-0838-remove-unique-absent.md §2). Pure finite first-order; no induction.
--
-- Verified under Lean 4.30.0 (core only, no Mathlib).

namespace UnixFs.Dir

variable {Disk : Type} {NameT : Type}
variable (slotInode : Disk → Int → Int → Int)
variable (slotName  : Disk → Int → Int → NameT)

-- No two distinct live in-range slots share a name (at block 5).
def uniq (d : Disk) : Prop :=
  ∀ i j : Int, 0 ≤ i → i < 16 → 0 ≤ j → j < 16 →
    slotInode d 5 i ≠ 0 → slotInode d 5 i < 32 →
    slotInode d 5 j ≠ 0 → slotInode d 5 j < 32 →
    slotName d 5 i = slotName d 5 j → i = j

-- Every block-5 slot decodes to an inode < 32.
def slots_lt32 (d : Disk) : Prop :=
  ∀ k : Int, 0 ≤ k → k < 16 → slotInode d 5 k < 32

-- ---- ESTABLISH ----

theorem establish_uniq (d : Disk)
    (hdead : ∀ k : Int, 0 ≤ k → k < 16 → slotInode d 5 k = 0) :
    uniq slotInode slotName d := by
  intro i j hi0 hi1 _ _ hil _ _ _ _
  exact absurd (hdead i hi0 hi1) hil

theorem establish_slots_lt32 (d : Disk)
    (hdead : ∀ k : Int, 0 ≤ k → k < 16 → slotInode d 5 k = 0) :
    slots_lt32 slotInode d := by
  intro k hk0 hk1
  rw [hdead k hk0 hk1]; decide

-- ---- FRAME (block-5 decode unchanged) ----

theorem frame_preserves_uniq (d0 d1 : Disk)
    (h0 : uniq slotInode slotName d0)
    (hfr : ∀ k : Int, 0 ≤ k → k < 16 →
       slotInode d1 5 k = slotInode d0 5 k ∧ slotName d1 5 k = slotName d0 5 k) :
    uniq slotInode slotName d1 := by
  intro i j hi0 hi1 hj0 hj1 hil hilt hjl hjlt hnm
  obtain ⟨hii, hin⟩ := hfr i hi0 hi1
  obtain ⟨hji, hjn⟩ := hfr j hj0 hj1
  refine h0 i j hi0 hi1 hj0 hj1 ?_ ?_ ?_ ?_ ?_
  · rw [← hii]; exact hil
  · rw [← hii]; exact hilt
  · rw [← hji]; exact hjl
  · rw [← hji]; exact hjlt
  · rw [← hin, ← hjn]; exact hnm

theorem frame_preserves_slots_lt32 (d0 d1 : Disk)
    (h0 : slots_lt32 slotInode d0)
    (hfr : ∀ k : Int, 0 ≤ k → k < 16 → slotInode d1 5 k = slotInode d0 5 k) :
    slots_lt32 slotInode d1 := by
  intro k hk0 hk1
  rw [hfr k hk0 hk1]; exact h0 k hk0 hk1

-- ---- ZERO (slot s cleared, rest framed) ----

theorem zero_preserves_uniq (d0 d1 : Disk) (s : Int)
    (h0 : uniq slotInode slotName d0)
    (hs0 : slotInode d1 5 s = 0)
    (hfr : ∀ k : Int, 0 ≤ k → k < 16 → k ≠ s →
       slotInode d1 5 k = slotInode d0 5 k ∧ slotName d1 5 k = slotName d0 5 k) :
    uniq slotInode slotName d1 := by
  intro i j hi0 hi1 hj0 hj1 hil hilt hjl hjlt hnm
  have his : i ≠ s := fun h => hil (h ▸ hs0)
  have hjs : j ≠ s := fun h => hjl (h ▸ hs0)
  obtain ⟨hii, hin⟩ := hfr i hi0 hi1 his
  obtain ⟨hji, hjn⟩ := hfr j hj0 hj1 hjs
  refine h0 i j hi0 hi1 hj0 hj1 ?_ ?_ ?_ ?_ ?_
  · rw [← hii]; exact hil
  · rw [← hii]; exact hilt
  · rw [← hji]; exact hjl
  · rw [← hji]; exact hjlt
  · rw [← hin, ← hjn]; exact hnm

theorem zero_preserves_slots_lt32 (d0 d1 : Disk) (s : Int)
    (h0 : slots_lt32 slotInode d0)
    (hs0 : slotInode d1 5 s = 0)
    (hfr : ∀ k : Int, 0 ≤ k → k < 16 → k ≠ s → slotInode d1 5 k = slotInode d0 5 k) :
    slots_lt32 slotInode d1 := by
  intro k hk0 hk1
  by_cases hks : k = s
  · rw [hks, hs0]; decide
  · rw [hfr k hk0 hk1 hks]; exact h0 k hk0 hk1

-- ---- INSERT (slot s becomes live with a fresh name, rest framed) ----

-- nm-free form: the inserted name is `slotName d1 5 s` itself, so the fact is
-- triggerable on [slotName d1 5 s, uniq d0] (no untriggerable name binder).
theorem insert_preserves_uniq_folded (d0 d1 : Disk) (s : Int)
    (h0 : uniq slotInode slotName d0)
    (_hs : 0 ≤ s ∧ s < 16)
    (hfresh : ∀ k : Int, 0 ≤ k → k < 16 →
       slotInode d0 5 k ≠ 0 → slotInode d0 5 k < 32 → slotName d0 5 k ≠ slotName d1 5 s)
    (hfr : ∀ k : Int, 0 ≤ k → k < 16 → k ≠ s →
       slotInode d1 5 k = slotInode d0 5 k ∧ slotName d1 5 k = slotName d0 5 k)
    (_hslt : slotInode d1 5 s ≠ 0 → slotInode d1 5 s < 32) :
    uniq slotInode slotName d1 := by
  intro i j hi0 hi1 hj0 hj1 hil hilt hjl hjlt hnm
  by_cases his : i = s <;> by_cases hjs : j = s
  · rw [his, hjs]
  · -- i = s, j ≠ s: slot j has the inserted name and is live on d0 -> contradicts fresh
    exfalso
    obtain ⟨hji, hjn⟩ := hfr j hj0 hj1 hjs
    have hjnm : slotName d0 5 j = slotName d1 5 s := by rw [← hjn, ← hnm, his]
    exact hfresh j hj0 hj1 (by rw [← hji]; exact hjl) (by rw [← hji]; exact hjlt) hjnm
  · -- j = s, i ≠ s: symmetric
    exfalso
    obtain ⟨hii, hin⟩ := hfr i hi0 hi1 his
    have hinm : slotName d0 5 i = slotName d1 5 s := by rw [← hin, hnm, hjs]
    exact hfresh i hi0 hi1 (by rw [← hii]; exact hil) (by rw [← hii]; exact hilt) hinm
  · -- both ≠ s
    obtain ⟨hii, hin⟩ := hfr i hi0 hi1 his
    obtain ⟨hji, hjn⟩ := hfr j hj0 hj1 hjs
    refine h0 i j hi0 hi1 hj0 hj1 ?_ ?_ ?_ ?_ ?_
    · rw [← hii]; exact hil
    · rw [← hii]; exact hilt
    · rw [← hji]; exact hjl
    · rw [← hji]; exact hjlt
    · rw [← hin, ← hjn]; exact hnm

theorem insert_preserves_slots_lt32 (d0 d1 : Disk) (s : Int)
    (h0 : slots_lt32 slotInode d0)
    (_hs : 0 ≤ s ∧ s < 16)
    (hslt : slotInode d1 5 s < 32)
    (hfr : ∀ k : Int, 0 ≤ k → k < 16 → k ≠ s → slotInode d1 5 k = slotInode d0 5 k) :
    slots_lt32 slotInode d1 := by
  intro k hk0 hk1
  by_cases hks : k = s
  · rw [hks]; exact hslt
  · rw [hfr k hk0 hk1 hks]; exact h0 k hk0 hk1

end UnixFs.Dir
