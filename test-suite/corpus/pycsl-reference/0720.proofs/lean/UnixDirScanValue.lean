-- Lean 4 cross-validation twin of the read-side dir_scan_result value marker.
-- Verified under core Lean (no Mathlib). No sorry.
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

def dirLookup (d : Disk) (blk : Int) (name : NameT) : Int :=
  scan slotInode slotName d blk name 16 (-1)

-- The read-side MARKER: dir_scan_result d blk name r ≜ r is the bounded scan result.
def dirScanResult (d : Disk) (blk : Int) (name : NameT) (r : Int) : Prop :=
  scan slotInode slotName d blk name 16 (-1) = r

-- dir_scan_result_value: the marker carries dirLookup = r. (zero TCB)
theorem dir_scan_result_value
    (d : Disk) (blk : Int) (name : NameT) (r : Int)
    (h : dirScanResult slotInode slotName d blk name r) :
    dirLookup slotInode slotName d blk name = r := by
  unfold dirLookup dirScanResult at *; exact h

-- dir_scan_result_intro (definitional): the marker from the closed scan result.
theorem dir_scan_result_intro
    (d : Disk) (blk : Int) (name : NameT) (r : Int)
    (h : scan slotInode slotName d blk name 16 (-1) = r) :
    dirScanResult slotInode slotName d blk name r := by
  unfold dirScanResult; exact h

-- ===== Prefix-marker loop-carry rungs =====
def dirScanPrefix (d : Disk) (blk : Int) (name : NameT) (i : Int) (r : Int) : Prop :=
  (0 ≤ i ∧ i ≤ 16) ∧ scan slotInode slotName d blk name i.toNat (-1) = r

theorem dir_scan_prefix_base (d : Disk) (blk : Int) (name : NameT) :
    dirScanPrefix slotInode slotName d blk name 0 (-1) := by
  unfold dirScanPrefix; refine ⟨⟨by decide, by decide⟩, ?_⟩; rfl

theorem dir_scan_prefix_step
    (d : Disk) (blk : Int) (name : NameT) (i : Int) (r : Int)
    (hi : 0 ≤ i ∧ i < 16)
    (hpre : dirScanPrefix slotInode slotName d blk name i r) :
    ( (slotInode d blk i ≠ 0 ∧ slotInode d blk i < 32 ∧ slotName d blk i = name)
        → dirScanPrefix slotInode slotName d blk name (i+1) (slotInode d blk i) ) ∧
    ( ¬(slotInode d blk i ≠ 0 ∧ slotInode d blk i < 32 ∧ slotName d blk i = name)
        → dirScanPrefix slotInode slotName d blk name (i+1) r ) := by
  obtain ⟨_, hpre⟩ := hpre
  have hi0 : 0 ≤ i := hi.1
  have hni : (i+1).toNat = (i.toNat) + 1 := by omega
  have hzi : Int.ofNat (i.toNat) = i := Int.toNat_of_nonneg hi0
  constructor
  · intro hg
    refine ⟨⟨by omega, by omega⟩, ?_⟩
    rw [hni]; unfold scan; rw [hpre]; rw [hzi]; rw [if_pos hg]
  · intro hng
    refine ⟨⟨by omega, by omega⟩, ?_⟩
    rw [hni]; unfold scan; rw [hpre]; rw [hzi]; rw [if_neg hng]

theorem dir_scan_prefix_close
    (d : Disk) (blk : Int) (name : NameT) (r : Int)
    (h : dirScanPrefix slotInode slotName d blk name 16 r) :
    dirLookup slotInode slotName d blk name = r := by
  obtain ⟨_, h⟩ := h
  unfold dirLookup
  have : (16 : Int).toNat = 16 := by decide
  rw [this] at h; exact h

end UnixFs.Dir

#print axioms UnixFs.Dir.dir_scan_result_value
#print axioms UnixFs.Dir.dir_scan_result_intro
#print axioms UnixFs.Dir.dir_scan_prefix_base
#print axioms UnixFs.Dir.dir_scan_prefix_step
#print axioms UnixFs.Dir.dir_scan_prefix_close
