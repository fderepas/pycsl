-- /tmp/dirscan/UnixDirScan.lean
--
-- Lean 4 cross-validation twin of UnixFs.Dir.scan_reflects_present (gap-9).
-- Same induction on the prefix length with a per-slot case split.
--
-- Verified under Lean 4.30.0 (core only, no Mathlib). No sorry, no axioms.

namespace UnixFs.Dir

variable {Disk : Type} {NameT : Type}
variable (slotInode : Disk → Int → Int → Int)
variable (slotName  : Disk → Int → Int → NameT)
variable [DecidableEq NameT]

-- A slot k is a live match for `name` in block `blk`.
def slotMatches (d : Disk) (blk : Int) (name : NameT) (k : Int) : Prop :=
  slotInode d blk k ≠ 0 ∧ slotInode d blk k < 32 ∧ slotName d blk k = name

-- The running scan over the first i slots, mirroring _dir_lookup's loop body.
-- Recurse first (prefix j), then test slot j: keeps the LAST match, exactly
-- like _dir_lookup.
def scan (d : Disk) (blk : Int) (name : NameT) : Nat → Int → Int
  | 0,     found => found
  | (j+1), found =>
      let f := scan d blk name j found
      let zj : Int := Int.ofNat j
      if slotInode d blk zj ≠ 0 ∧ slotInode d blk zj < 32 ∧ slotName d blk zj = name
      then slotInode d blk zj
      else f

-- Faithful model fact: a decoded inode number is non-negative (unsigned bytes).
-- The single semantic assumption beyond the scan structure.
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
    · -- guard true: slot j is a live match; result = slotInode j.
      rw [if_pos hguard]
      obtain ⟨hne, hlt, heq⟩ := hguard
      have hm : slotMatches slotInode slotName d blk name (Int.ofNat j) := ⟨hne, hlt, heq⟩
      have hinn : 0 ≤ slotInode d blk (Int.ofNat j) := hnn (Int.ofNat j)
      refine ⟨⟨fun _ => ⟨Int.ofNat j, by omega, by omega, hm⟩, fun _ => by omega⟩,
              fun _ => by omega⟩
    · -- guard false: result = scan over prefix j.
      rw [if_neg hguard]
      refine ⟨?_, ihrng⟩
      rw [ihiff]
      constructor
      · rintro ⟨k, hk0, hkj, hm⟩
        exact ⟨k, hk0, by omega, hm⟩
      · rintro ⟨k, hk0, hkj1, hm⟩
        -- k < j+1; exclude k = j since slot j is no match.
        rcases (show k < Int.ofNat j ∨ k = Int.ofNat j by omega) with hklt | hkeq
        · exact ⟨k, hk0, hklt, hm⟩
        · exfalso; rw [hkeq] at hm; exact hguard hm

-- The registered axiom: directory width 16. dir_lookup := scan ... 16 (-1).
def dirLookup (d : Disk) (blk : Int) (name : NameT) : Int :=
  scan slotInode slotName d blk name 16 (-1)

theorem scan_reflects_present
    (d : Disk) (blk : Int) (name : NameT)
    (hnn : ∀ k, 0 ≤ slotInode d blk k) :
    (dirLookup slotInode slotName d blk name ≥ 0)
      ↔ (∃ k : Int, 0 ≤ k ∧ k < 16 ∧ slotMatches slotInode slotName d blk name k) := by
  have h := (scan_reflects_prefix slotInode slotName d blk name hnn 16).1
  simpa [dirLookup] using h

-- UnixFs.Dir.dir_lookup_present_witness (M4 rename — add+remove coexistence fix).
-- The NARROW-TRIGGER presence corollary: a single explicit witness slot k that is
-- a live in-range match for `name` gives dirLookup ≥ 0 with NO existential in the
-- goal — the `←` direction of scan_reflects_present specialised to a given witness.
-- sys_rename uses it so the presence (newpath) discharges in O(1) on the
-- materialised witness slot, never introducing the matches-existential that (for
-- the absent oldpath) would interleave with the absence axioms.
-- nm-free: the looked-up name IS the witness slot's own name (slotName d blk k), so the
-- WhyML axiom triggers on [slotInode k, slotName k] — once per slot, not per (name,slot).
theorem dir_lookup_present_witness
    (d : Disk) (blk : Int) (k : Int)
    (hnn : ∀ k, 0 ≤ slotInode d blk k)
    (hk : 0 ≤ k ∧ k < 16)
    (hne : slotInode d blk k ≠ 0) (hlt : slotInode d blk k < 32) :
    dirLookup slotInode slotName d blk (slotName d blk k) ≥ 0 := by
  rw [scan_reflects_present slotInode slotName d blk (slotName d blk k) hnn]
  exact ⟨k, hk.1, hk.2, ⟨hne, hlt, rfl⟩⟩

-- UnixFs.Dir.dir_lookup_present_zero_frame (M4 rename — scalar presence carry).
-- Zeroing slot s preserves the presence of any OTHER name: the present witness for
-- `name` in d0 cannot be s (its name is `name` ≠ slotName d0 5 s), so it survives the
-- frame and still matches in d1. Lets sys_rename carry dir_lookup(newpath) ≥ 0 across
-- the final old-slot zero as a scalar (presence in post-write, absence in post-zero).
theorem dir_lookup_present_zero_frame
    (d0 d1 : Disk) (s : Int) (name : NameT)
    (hnn0 : ∀ k, 0 ≤ slotInode d0 5 k) (hnn1 : ∀ k, 0 ≤ slotInode d1 5 k)
    (hs : 0 ≤ s ∧ s < 16) (hsdead : slotInode d1 5 s = 0)
    (hframe : ∀ k : Int, 0 ≤ k → k < 16 → k ≠ s →
        slotInode d1 5 k = slotInode d0 5 k ∧ slotName d1 5 k = slotName d0 5 k)
    (hname : name ≠ slotName d0 5 s)
    (hpres : dirLookup slotInode slotName d0 5 name ≥ 0) :
    dirLookup slotInode slotName d1 5 name ≥ 0 := by
  rw [scan_reflects_present slotInode slotName d0 5 name hnn0] at hpres
  obtain ⟨k, hk0, hk16, hne, hlt, hnm⟩ := hpres
  rw [scan_reflects_present slotInode slotName d1 5 name hnn1]
  have hks : k ≠ s := by intro he; subst he; exact hname hnm.symm
  obtain ⟨hi, hn⟩ := hframe k hk0 hk16 hks
  exact ⟨k, hk0, hk16, by rw [hi]; exact hne, by rw [hi]; exact hlt, by rw [hn]; exact hnm⟩

-- The unsigned-byte fact, UnixFs.Dir.slot_inode_nonneg (registry's
-- slot_inode_nonneg axiom): a decoded directory-slot inode is non-negative.
-- This is the `hnn` hypothesis of scan_reflects_present, proven here about the
-- CONCRETE decode `slotInodeConcrete` (a big-endian uint32 read of the 4 inode
-- bytes), >= 0 by non-negativity of unsigned byte values. The WhyML axiom
-- `forall disk blk k. slot_inode disk blk k >= 0` reflects exactly this.
def slotInodeConcrete (byte : Int → Int → Int → Int) (d blk k : Int) : Int :=
  byte d blk (blk*512 + k*32 + 0) * 16777216
  + byte d blk (blk*512 + k*32 + 1) * 65536
  + byte d blk (blk*512 + k*32 + 2) * 256
  + byte d blk (blk*512 + k*32 + 3)

theorem slot_inode_nonneg
    (byte : Int → Int → Int → Int)
    (byte_unsigned : ∀ d blk p, 0 ≤ byte d blk p ∧ byte d blk p ≤ 255)
    (d blk k : Int) :
    0 ≤ slotInodeConcrete byte d blk k := by
  unfold slotInodeConcrete
  have h0 := byte_unsigned d blk (blk*512 + k*32 + 0)
  have h1 := byte_unsigned d blk (blk*512 + k*32 + 1)
  have h2 := byte_unsigned d blk (blk*512 + k*32 + 2)
  have h3 := byte_unsigned d blk (blk*512 + k*32 + 3)
  omega

end UnixFs.Dir
