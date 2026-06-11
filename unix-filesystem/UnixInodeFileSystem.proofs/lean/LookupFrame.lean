-- /tmp/dirscan/LookupFrame.lean
--
-- Lean 4 cross-validation twin of UnixFs.Dir.lookup_frame (gap-17, the content
-- round-trip wall). The dir_lookup FRAME/CONGRUENCE lemma: dir_lookup depends
-- ONLY on the 16 per-slot decodes (slot_inode / slot_name over k in [0,16)) of
-- the block. Two disks that agree on every per-slot decode of `blk` therefore
-- produce the same dir_lookup result.
--
-- Mirrors UnixDirScan.lean exactly: same abstract Disk/NameT, the same abstract
-- slotInode/slotName decode functions, the same `scan` recursion (recurse on
-- the prefix, then test slot j, keeping the LAST live match), and the same
-- dirLookup := scan ... 16 (-1). Proven by induction on the prefix length i:
-- scan reads only slots j < i, so per-slot agreement on [0,i) suffices.
--
-- Lean 4.30.0 core, no Mathlib. #print axioms ⊆ {propext, Quot.sound}. No sorry.

namespace UnixFs.Dir

variable {Disk : Type} {NameT : Type}
variable (slotInode : Disk → Int → Int → Int)
variable (slotName  : Disk → Int → Int → NameT)
variable [DecidableEq NameT]

-- The running scan over the first i slots, mirroring _dir_lookup's loop body.
-- Recurse first (prefix j), then test slot j: keeps the LAST match, exactly
-- like _dir_lookup. Identical to UnixDirScan.lean's `scan`.
def scan (d : Disk) (blk : Int) (name : NameT) : Nat → Int → Int
  | 0,     found => found
  | (j+1), found =>
      let f := scan d blk name j found
      let zj : Int := Int.ofNat j
      if slotInode d blk zj ≠ 0 ∧ slotInode d blk zj < 32 ∧ slotName d blk zj = name
      then slotInode d blk zj
      else f

-- dir_lookup := scan ... 16 (-1). Directory width 16, as registered.
def dirLookup (d : Disk) (blk : Int) (name : NameT) : Int :=
  scan slotInode slotName d blk name 16 (-1)

-- Frame on the running scan: if d0 and d1 agree on every per-slot decode for
-- k in [0,i), then scan over the first i slots agrees from any common `found`.
-- The scan over i slots reads slot_inode/slot_name only at j < i, so per-slot
-- agreement on the prefix [0,i) is exactly what is needed. By induction on i.
theorem scan_frame
    (d0 d1 : Disk) (blk : Int) (name : NameT)
    (hi : ∀ k : Int, 0 ≤ k → k < 16 → slotInode d1 blk k = slotInode d0 blk k)
    (hn : ∀ k : Int, 0 ≤ k → k < 16 → slotName  d1 blk k = slotName  d0 blk k) :
    ∀ (i : Nat), (Int.ofNat i ≤ 16) → ∀ found : Int,
      scan slotInode slotName d1 blk name i found
        = scan slotInode slotName d0 blk name i found := by
  intro i
  induction i with
  | zero =>
    intro _ found
    simp only [scan]
  | succ j ih =>
    intro hle found
    have hcast : (Int.ofNat (j+1) : Int) = Int.ofNat j + 1 := by exact_mod_cast rfl
    have hofj : (0 : Int) ≤ Int.ofNat j := Int.natCast_nonneg j
    have hjle : Int.ofNat j ≤ 16 := by omega
    have hjlt : Int.ofNat j < 16 := by omega
    -- the two per-slot decodes at slot j coincide
    have hI : slotInode d1 blk (Int.ofNat j) = slotInode d0 blk (Int.ofNat j) :=
      hi (Int.ofNat j) hofj hjlt
    have hN : slotName  d1 blk (Int.ofNat j) = slotName  d0 blk (Int.ofNat j) :=
      hn (Int.ofNat j) hofj hjlt
    simp only [scan]
    rw [ih hjle found, hI, hN]

theorem lookup_frame
    (d0 d1 : Disk) (blk : Int) (name : NameT)
    (hi : ∀ k : Int, 0 ≤ k → k < 16 → slotInode d1 blk k = slotInode d0 blk k)
    (hn : ∀ k : Int, 0 ≤ k → k < 16 → slotName  d1 blk k = slotName  d0 blk k) :
    dirLookup slotInode slotName d1 blk name
      = dirLookup slotInode slotName d0 blk name := by
  unfold dirLookup
  exact scan_frame slotInode slotName d0 d1 blk name hi hn 16 (by decide) (-1)

#print axioms lookup_frame

end UnixFs.Dir
