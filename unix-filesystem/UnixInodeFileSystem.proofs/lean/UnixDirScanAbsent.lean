-- unix-filesystem/UnixInodeFileSystem.proofs/lean/UnixDirScanAbsent.lean
--
-- Lean 4 cross-validation twin of UnixFs.Dir.remove_reflects_absent (gap-11).
-- Reuses the gap-9 scan_reflects_prefix induction, then derives the ABSENCE
-- direction. Verified under Lean 4.30.0 (core only, no Mathlib).

namespace UnixFs.Dir

variable {Disk : Type} {NameT : Type}
variable (slotInode : Disk → Int → Int → Int)
variable (slotName  : Disk → Int → Int → NameT)
variable [DecidableEq NameT]

def slotMatches (d : Disk) (blk : Int) (name : NameT) (k : Int) : Prop :=
  slotInode d blk k ≠ 0 ∧ slotInode d blk k < 32 ∧ slotName d blk k = name

def scan (d : Disk) (blk : Int) (name : NameT) : Nat → Int → Int
  | 0,     found => found
  | (j+1), found =>
      let f := scan d blk name j found
      let zj : Int := Int.ofNat j
      if slotInode d blk zj ≠ 0 ∧ slotInode d blk zj < 32 ∧ slotName d blk zj = name
      then slotInode d blk zj
      else f

-- gap-9 lemma, verbatim.
theorem scan_reflects_prefix
    (d : Disk) (blk : Int) (name : NameT)
    (hnn : ∀ k, 0 ≤ slotInode d blk k) :
    ∀ i : Nat,
      ((scan slotInode slotName d blk name i (-1) ≥ 0)
        ↔ (∃ k : Int, 0 ≤ k ∧ k < Int.ofNat i ∧
              slotMatches slotInode slotName d blk name k))
      ∧ (scan slotInode slotName d blk name i (-1) ≥ 0 →
           scan slotInode slotName d blk name i (-1) < 32) := by
  intro i
  induction i with
  | zero =>
    simp only [scan]
    constructor
    · constructor
      · intro h; exact absurd h (by decide)
      · rintro ⟨k, hk0, hki, _⟩; simp at hki; omega
    · intro h; exact absurd h (by decide)
  | succ j ih =>
    obtain ⟨ihiff, ihrng⟩ := ih
    simp only [scan]
    have hofj : (0 : Int) ≤ Int.ofNat j := Int.natCast_nonneg j
    have hsucc : (Int.ofNat (j+1) : Int) = Int.ofNat j + 1 := by exact_mod_cast rfl
    by_cases hguard :
        slotInode d blk (Int.ofNat j) ≠ 0 ∧ slotInode d blk (Int.ofNat j) < 32 ∧
          slotName d blk (Int.ofNat j) = name
    · rw [if_pos hguard]
      obtain ⟨hne, hlt, heq⟩ := hguard
      have hm : slotMatches slotInode slotName d blk name (Int.ofNat j) := ⟨hne, hlt, heq⟩
      have hinn : 0 ≤ slotInode d blk (Int.ofNat j) := hnn (Int.ofNat j)
      refine ⟨⟨fun _ => ⟨Int.ofNat j, by omega, by omega, hm⟩, fun _ => by omega⟩,
              fun _ => by omega⟩
    · rw [if_neg hguard]
      refine ⟨?_, ihrng⟩
      rw [ihiff]
      constructor
      · rintro ⟨k, hk0, hkj, hm⟩
        exact ⟨k, hk0, by omega, hm⟩
      · rintro ⟨k, hk0, hkj1, hm⟩
        rcases (show k < Int.ofNat j ∨ k = Int.ofNat j by omega) with hklt | hkeq
        · exact ⟨k, hk0, hklt, hm⟩
        · exfalso; rw [hkeq] at hm; exact hguard hm

def dirLookup (d : Disk) (blk : Int) (name : NameT) : Int :=
  scan slotInode slotName d blk name 16 (-1)

-- gap-11: the ABSENCE reflection.
-- The `hnn` antecedent is the unbounded slot-decode non-negativity (gap-9's
-- registered UnixFs.Dir.slot_inode_nonneg axiom — same form), kept so the
-- shared scan_reflects_prefix infrastructure applies. The remove-witness
-- (hwit) + uniqueness (huniq) make the bounded matches-set empty.
theorem remove_reflects_absent
    (d : Disk) (blk : Int) (name : NameT) (s : Int)
    (hnn : ∀ k, 0 ≤ slotInode d blk k)
    (hs  : 0 ≤ s ∧ s < 16)
    (hwit : slotInode d blk s = 0)
    (huniq : ∀ k : Int, 0 ≤ k → k < 16 → k ≠ s →
        slotName d blk k = name → slotInode d blk k = 0) :
    dirLookup slotInode slotName d blk name < 0 := by
  unfold dirLookup
  -- the matches-set over [0,16) is empty.
  have hempty : ¬ (∃ k : Int, 0 ≤ k ∧ k < Int.ofNat 16 ∧
      slotMatches slotInode slotName d blk name k) := by
    rintro ⟨k, hk0, hk16, hne, _hlt, hnm⟩
    simp only [show (Int.ofNat 16 : Int) = 16 from rfl] at hk16
    by_cases hks : k = s
    · rw [hks] at hne; exact hne hwit
    · exact hne (huniq k hk0 hk16 hks hnm)
  have hiff := (scan_reflects_prefix slotInode slotName d blk name hnn 16).1
  -- scan ≥ 0 would give a match (contradiction), so scan < 0.
  have hnotge : ¬ (scan slotInode slotName d blk name 16 (-1) ≥ 0) :=
    fun hge => hempty (hiff.mp hge)
  omega

end UnixFs.Dir

#print axioms UnixFs.Dir.remove_reflects_absent
