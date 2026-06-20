-- Lean 4 cross-validation twin of the SLOT-INDEX dir_find_slot_result marker.
-- _dir_find_slot returns the INDEX (0..15) of the LAST live slot matching
-- `name`, or -1 (the slot-index dual of _dir_lookup's INODE result in
-- UnixDirScanValue.lean). Verified under core Lean (no Mathlib). No sorry.
namespace UnixFs.Dir

variable {Disk : Type} {NameT : Type}
variable (slotInode : Disk → Int → Int → Int)
variable (slotName  : Disk → Int → Int → NameT)
variable [DecidableEq NameT]

def slotMatches (d : Disk) (blk : Int) (name : NameT) (k : Int) : Prop :=
  slotInode d blk k ≠ 0 ∧ slotInode d blk k < 32 ∧ slotName d blk k = name

-- The running SLOT-INDEX scan: keeps the LAST matching INDEX (when slot j
-- matches, found becomes the INDEX zj, not the inode).
def fscan (d : Disk) (blk : Int) (name : NameT) : Nat → Int → Int
  | 0,     found => found
  | (j+1), found =>
      let f := fscan d blk name j found
      let zj : Int := Int.ofNat j
      if slotInode d blk zj ≠ 0 ∧ slotInode d blk zj < 32 ∧ slotName d blk zj = name
      then zj
      else f

def dirFindSlot (d : Disk) (blk : Int) (name : NameT) : Int :=
  fscan slotInode slotName d blk name 16 (-1)

-- The carry invariant: the result is either an in-range live-match INDEX, or
-- the unchanged start value.
theorem fscan_result_matches
    (d : Disk) (blk : Int) (name : NameT) (i : Nat) (start : Int) :
    let r := fscan slotInode slotName d blk name i start
    ((0 ≤ r ∧ r < Int.ofNat i ∧ slotMatches slotInode slotName d blk name r) ∨ r = start) := by
  induction i with
  | zero => simp [fscan]
  | succ j IH =>
      simp only [fscan, slotMatches] at IH ⊢
      have hsucc : Int.ofNat (j + 1) = Int.ofNat j + 1 := rfl
      split
      · rename_i hg
        left
        refine ⟨Int.natCast_nonneg j, ?_, hg⟩
        rw [hsucc]; omega
      · rcases IH with ⟨hr0, hrlt, hm⟩ | heq
        · left
          refine ⟨hr0, ?_, hm⟩
          rw [hsucc]; omega
        · right; exact heq

-- The MARKER: dir_find_slot_result d blk name r ≜ r is the bounded index-scan result.
def dirFindSlotResult (d : Disk) (blk : Int) (name : NameT) (r : Int) : Prop :=
  fscan slotInode slotName d blk name 16 (-1) = r

-- dir_find_slot_result_intro (definitional): the marker from the closed result.
theorem dir_find_slot_result_intro
    (d : Disk) (blk : Int) (name : NameT) (r : Int)
    (h : fscan slotInode slotName d blk name 16 (-1) = r) :
    dirFindSlotResult slotInode slotName d blk name r := by
  unfold dirFindSlotResult; exact h

-- dir_find_slot_result_value (load-bearing slot-index fidelity): when r ≥ 0,
-- slot r decodes to a live entry named `name`.
theorem dir_find_slot_result_value
    (d : Disk) (blk : Int) (name : NameT) (r : Int)
    (hmk : dirFindSlotResult slotInode slotName d blk name r)
    (hpos : r ≥ 0) :
    slotInode d blk r ≠ 0 ∧ slotName d blk r = name := by
  unfold dirFindSlotResult at hmk
  have hinv := fscan_result_matches slotInode slotName d blk name 16 (-1)
  simp only [slotMatches] at hinv
  rw [hmk] at hinv
  rcases hinv with ⟨_, _, hi, _, hn⟩ | heq
  · exact ⟨hi, hn⟩
  · omega

-- dir_find_slot_result_range (definitional): r is in [-1, 16).
theorem dir_find_slot_result_range
    (d : Disk) (blk : Int) (name : NameT) (r : Int)
    (hmk : dirFindSlotResult slotInode slotName d blk name r) :
    -1 ≤ r ∧ r < 16 := by
  unfold dirFindSlotResult at hmk
  have hinv := fscan_result_matches slotInode slotName d blk name 16 (-1)
  simp only [slotMatches] at hinv
  rw [hmk] at hinv
  rcases hinv with ⟨hr0, hrlt, _⟩ | heq
  · constructor <;> omega
  · constructor <;> omega

-- ===== Prefix-marker loop-carry rungs =====
def dirFindSlotPrefix (d : Disk) (blk : Int) (name : NameT) (i : Int) (r : Int) : Prop :=
  (0 ≤ i ∧ i ≤ 16) ∧ fscan slotInode slotName d blk name i.toNat (-1) = r

theorem dir_find_slot_prefix_base (d : Disk) (blk : Int) (name : NameT) :
    dirFindSlotPrefix slotInode slotName d blk name 0 (-1) := by
  unfold dirFindSlotPrefix; refine ⟨⟨by decide, by decide⟩, ?_⟩; rfl

theorem dir_find_slot_prefix_step
    (d : Disk) (blk : Int) (name : NameT) (i : Int) (r : Int)
    (hi : 0 ≤ i ∧ i < 16)
    (hpre : dirFindSlotPrefix slotInode slotName d blk name i r) :
    ( (slotInode d blk i ≠ 0 ∧ slotInode d blk i < 32 ∧ slotName d blk i = name)
        → dirFindSlotPrefix slotInode slotName d blk name (i+1) i ) ∧
    ( ¬(slotInode d blk i ≠ 0 ∧ slotInode d blk i < 32 ∧ slotName d blk i = name)
        → dirFindSlotPrefix slotInode slotName d blk name (i+1) r ) := by
  obtain ⟨_, hpre⟩ := hpre
  have hi0 : 0 ≤ i := hi.1
  have hni : (i+1).toNat = (i.toNat) + 1 := by omega
  have hzi : Int.ofNat (i.toNat) = i := Int.toNat_of_nonneg hi0
  constructor
  · intro hg
    refine ⟨⟨by omega, by omega⟩, ?_⟩
    rw [hni]; unfold fscan; rw [hpre]; rw [hzi]; rw [if_pos hg]
  · intro hng
    refine ⟨⟨by omega, by omega⟩, ?_⟩
    rw [hni]; unfold fscan; rw [hpre]; rw [hzi]; rw [if_neg hng]

theorem dir_find_slot_prefix_close
    (d : Disk) (blk : Int) (name : NameT) (r : Int)
    (h : dirFindSlotPrefix slotInode slotName d blk name 16 r) :
    dirFindSlotResult slotInode slotName d blk name r := by
  obtain ⟨_, h⟩ := h
  unfold dirFindSlotResult
  have : (16 : Int).toNat = 16 := by decide
  rw [this] at h; exact h

end UnixFs.Dir

#print axioms UnixFs.Dir.dir_find_slot_result_value
#print axioms UnixFs.Dir.dir_find_slot_result_intro
#print axioms UnixFs.Dir.dir_find_slot_result_range
#print axioms UnixFs.Dir.dir_find_slot_prefix_base
#print axioms UnixFs.Dir.dir_find_slot_prefix_step
#print axioms UnixFs.Dir.dir_find_slot_prefix_close
