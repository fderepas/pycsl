-- unix-filesystem/UnixInodeFileSystem.proofs/lean/DirLookupFrame.lean
--
-- Lean 4 cross-validation twin of UnixFs.Dir.dir_lookup_frame (M4 unlink reorder).
-- `dir_lookup` is the bounded 16-slot scan; its value depends only on the per-slot
-- decodes. So disks agreeing on every block-5 slot decode have equal dir_lookup —
-- letting sys_unlink carry `dir_lookup < 0` as a scalar across the block-freeing
-- loop (writes confined to block 0). Verified under Lean 4.30.0 (core, no Mathlib).

namespace UnixFs.Dir

variable {Disk : Type} {NameT : Type}
variable (slotInode : Disk → Int → Int → Int)
variable (slotName  : Disk → Int → Int → NameT)
variable [DecidableEq NameT]

-- scan, verbatim from UnixDirScanAbsent.lean.
def scan (d : Disk) (blk : Int) (name : NameT) : Nat → Int → Int
  | 0,     found => found
  | (j+1), found =>
      let f := scan d blk name j found
      let zj : Int := Int.ofNat j
      if slotInode d blk zj ≠ 0 ∧ slotInode d blk zj < 32 ∧ slotName d blk zj = name
      then slotInode d blk zj
      else f

def dir_lookup (d : Disk) (blk : Int) (name : NameT) : Int :=
  scan slotInode slotName d blk name 16 (-1)

theorem scan_frame (d0 d1 : Disk) (name : NameT) :
    ∀ i : Nat,
      (∀ j : Int, 0 ≤ j → j < Int.ofNat i →
         slotInode d1 5 j = slotInode d0 5 j ∧ slotName d1 5 j = slotName d0 5 j) →
      scan slotInode slotName d1 5 name i (-1)
        = scan slotInode slotName d0 5 name i (-1) := by
  intro i
  induction i with
  | zero => intro _; rfl
  | succ j ih =>
    intro hagree
    have hcast : (Int.ofNat (j + 1) : Int) = Int.ofNat j + 1 := by exact_mod_cast rfl
    obtain ⟨hi, hn⟩ := hagree (Int.ofNat j) (Int.natCast_nonneg j) (by rw [hcast]; omega)
    have iheq := ih (fun k hk0 hk1 => hagree k hk0 (by rw [hcast]; omega))
    simp only [scan]
    rw [hi, hn, iheq]

theorem dir_lookup_frame (d0 d1 : Disk) (name : NameT)
    (hframe : ∀ k : Int, 0 ≤ k → k < 16 →
       slotInode d1 5 k = slotInode d0 5 k ∧ slotName d1 5 k = slotName d0 5 k) :
    dir_lookup slotInode slotName d1 5 name = dir_lookup slotInode slotName d0 5 name := by
  unfold dir_lookup
  apply scan_frame
  intro j hj0 hj1
  exact hframe j hj0 (by simpa using hj1)

end UnixFs.Dir
