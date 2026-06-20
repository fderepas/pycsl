-- Lean 4 cross-validation twin of the FREE-SLOT-INDEX dir_find_free_result
-- marker. _dir_find_free scans the 16 slots and returns the INDEX (0..15) of
-- the LAST FREE slot (slot_inode = 0), or -1 (the free-slot dual of
-- _dir_find_slot's live-match INDEX in UnixDirFindSlotValue.lean). Unlike its
-- twin it reads ONLY slot_inode (no name decode), and the guard is the free
-- condition `slot_inode = 0`. Verified under core Lean (no Mathlib). No sorry.
namespace UnixFs.Dir

variable {Disk : Type}
variable (slotInode : Disk → Int → Int → Int)

def slotFree (d : Disk) (blk : Int) (k : Int) : Prop :=
  slotInode d blk k = 0

-- The running FREE-SLOT-INDEX scan: keeps the LAST free INDEX (when slot j is
-- free, found becomes the INDEX zj).
def ffscan (d : Disk) (blk : Int) : Nat → Int → Int
  | 0,     found => found
  | (j+1), found =>
      let f := ffscan d blk j found
      let zj : Int := Int.ofNat j
      if slotInode d blk zj = 0
      then zj
      else f

def dirFindFree (d : Disk) (blk : Int) : Int :=
  ffscan slotInode d blk 16 (-1)

-- The carry invariant: the result is either an in-range free INDEX, or the
-- unchanged start value.
theorem ffscan_result_free
    (d : Disk) (blk : Int) (i : Nat) (start : Int) :
    let r := ffscan slotInode d blk i start
    ((0 ≤ r ∧ r < Int.ofNat i ∧ slotFree slotInode d blk r) ∨ r = start) := by
  induction i with
  | zero => simp [ffscan]
  | succ j IH =>
      simp only [ffscan, slotFree] at IH ⊢
      have hsucc : Int.ofNat (j + 1) = Int.ofNat j + 1 := rfl
      split
      · rename_i hg
        left
        refine ⟨Int.natCast_nonneg j, ?_, hg⟩
        rw [hsucc]; omega
      · rcases IH with ⟨hr0, hrlt, hf⟩ | heq
        · left
          refine ⟨hr0, ?_, hf⟩
          rw [hsucc]; omega
        · right; exact heq

-- The MARKER: dir_find_free_result d blk r ≜ r is the bounded free-index-scan result.
def dirFindFreeResult (d : Disk) (blk : Int) (r : Int) : Prop :=
  ffscan slotInode d blk 16 (-1) = r

-- dir_find_free_result_intro (definitional).
theorem dir_find_free_result_intro
    (d : Disk) (blk : Int) (r : Int)
    (h : ffscan slotInode d blk 16 (-1) = r) :
    dirFindFreeResult slotInode d blk r := by
  unfold dirFindFreeResult; exact h

-- dir_find_free_result_value (load-bearing free-slot fidelity): when r ≥ 0,
-- slot r has slot_inode = 0.
theorem dir_find_free_result_value
    (d : Disk) (blk : Int) (r : Int)
    (hmk : dirFindFreeResult slotInode d blk r)
    (hpos : r ≥ 0) :
    slotInode d blk r = 0 := by
  unfold dirFindFreeResult at hmk
  have hinv := ffscan_result_free slotInode d blk 16 (-1)
  simp only [slotFree] at hinv
  rw [hmk] at hinv
  rcases hinv with ⟨_, _, hf⟩ | heq
  · exact hf
  · omega

-- dir_find_free_result_range (definitional): r is in [-1, 16).
theorem dir_find_free_result_range
    (d : Disk) (blk : Int) (r : Int)
    (hmk : dirFindFreeResult slotInode d blk r) :
    -1 ≤ r ∧ r < 16 := by
  unfold dirFindFreeResult at hmk
  have hinv := ffscan_result_free slotInode d blk 16 (-1)
  simp only [slotFree] at hinv
  rw [hmk] at hinv
  rcases hinv with ⟨hr0, hrlt, _⟩ | heq
  · constructor <;> omega
  · constructor <;> omega

-- ===== Prefix-marker loop-carry rungs =====
def dirFindFreePrefix (d : Disk) (blk : Int) (i : Int) (r : Int) : Prop :=
  (0 ≤ i ∧ i ≤ 16) ∧ ffscan slotInode d blk i.toNat (-1) = r

theorem dir_find_free_prefix_base (d : Disk) (blk : Int) :
    dirFindFreePrefix slotInode d blk 0 (-1) := by
  unfold dirFindFreePrefix; refine ⟨⟨by decide, by decide⟩, ?_⟩; rfl

theorem dir_find_free_prefix_step
    (d : Disk) (blk : Int) (i : Int) (r : Int)
    (hi : 0 ≤ i ∧ i < 16)
    (hpre : dirFindFreePrefix slotInode d blk i r) :
    ( slotInode d blk i = 0
        → dirFindFreePrefix slotInode d blk (i+1) i ) ∧
    ( slotInode d blk i ≠ 0
        → dirFindFreePrefix slotInode d blk (i+1) r ) := by
  obtain ⟨_, hpre⟩ := hpre
  have hi0 : 0 ≤ i := hi.1
  have hni : (i+1).toNat = (i.toNat) + 1 := by omega
  have hzi : Int.ofNat (i.toNat) = i := Int.toNat_of_nonneg hi0
  constructor
  · intro hg
    refine ⟨⟨by omega, by omega⟩, ?_⟩
    rw [hni]; unfold ffscan; rw [hpre]; rw [hzi]; rw [if_pos hg]
  · intro hng
    refine ⟨⟨by omega, by omega⟩, ?_⟩
    rw [hni]; unfold ffscan; rw [hpre]; rw [hzi]; rw [if_neg hng]

theorem dir_find_free_prefix_close
    (d : Disk) (blk : Int) (r : Int)
    (h : dirFindFreePrefix slotInode d blk 16 r) :
    dirFindFreeResult slotInode d blk r := by
  obtain ⟨_, h⟩ := h
  unfold dirFindFreeResult
  have : (16 : Int).toNat = 16 := by decide
  rw [this] at h; exact h

end UnixFs.Dir

#print axioms UnixFs.Dir.dir_find_free_result_value
#print axioms UnixFs.Dir.dir_find_free_result_intro
#print axioms UnixFs.Dir.dir_find_free_result_range
#print axioms UnixFs.Dir.dir_find_free_prefix_base
#print axioms UnixFs.Dir.dir_find_free_prefix_step
#print axioms UnixFs.Dir.dir_find_free_prefix_close
