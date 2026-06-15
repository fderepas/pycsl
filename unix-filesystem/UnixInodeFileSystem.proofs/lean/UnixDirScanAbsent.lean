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

-- Directory-uniqueness predicate at block 5 (matches DirInvariantMaintenance.uniq /
-- the registered UnixFs.Dir.uniq) and the slot-range invariant.
def uniq (d : Disk) : Prop :=
  ∀ i j : Int, 0 ≤ i → i < 16 → 0 ≤ j → j < 16 →
    slotInode d 5 i ≠ 0 → slotInode d 5 i < 32 →
    slotInode d 5 j ≠ 0 → slotInode d 5 j < 32 →
    slotName d 5 i = slotName d 5 j → i = j

def slots_lt32 (d : Disk) : Prop :=
  ∀ k : Int, 0 ≤ k → k < 16 → slotInode d 5 k < 32

-- UnixFs.Dir.dir_lookup_remove_absent (M4 rename — add+remove COEXISTENCE fix).
-- remove_unique_absent (witness from uniqueness) FUSED with remove_reflects_absent
-- (dir_lookup < 0), as one fact keyed on the removed slot. nm-free: the absent name
-- is the removed slot's old name slotName d0 5 s, so the WhyML axiom triggers on
-- [slotInode d1 5 s, slotInode d0 5 s], never on dir_lookup — so it does not match the
-- per-slot dir_lookup(slotName k) terms the presence witness creates.
theorem dir_lookup_remove_absent
    (d0 d1 : Disk) (s : Int)
    (hnn : ∀ j, 0 ≤ slotInode d1 5 j)
    (huniq : uniq slotInode slotName d0) (hlt32 : slots_lt32 slotInode d0)
    (hs : 0 ≤ s ∧ s < 16) (hs0live : slotInode d0 5 s ≠ 0) (hs1dead : slotInode d1 5 s = 0)
    (hframei : ∀ k : Int, 0 ≤ k → k < 16 → k ≠ s → slotInode d1 5 k = slotInode d0 5 k)
    (hframen : ∀ k : Int, 0 ≤ k → k < 16 → k ≠ s → slotName d1 5 k = slotName d0 5 k) :
    dirLookup slotInode slotName d1 5 (slotName d0 5 s) < 0 := by
  apply remove_reflects_absent slotInode slotName d1 5 (slotName d0 5 s) s hnn hs hs1dead
  -- witness: every other slot named (slotName d0 5 s) is dead on d1 (inlined uniqueness).
  intro k hk0 hk16 hks hname
  by_cases hz : slotInode d1 5 k = 0
  · exact hz
  · exfalso
    rw [hframei k hk0 hk16 hks] at hz
    rw [hframen k hk0 hk16 hks] at hname
    have hk32 : slotInode d0 5 k < 32 := hlt32 k hk0 hk16
    have hs32 : slotInode d0 5 s < 32 := hlt32 s hs.1 hs.2
    have heq : k = s := huniq k s hk0 hk16 hs.1 hs.2 hz hk32 hs0live hs32 hname
    exact hks heq

end UnixFs.Dir

#print axioms UnixFs.Dir.remove_reflects_absent
#print axioms UnixFs.Dir.dir_lookup_remove_absent
