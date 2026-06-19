/- Validation of the BLOCK-PARAMETERIZED form of the ROUTE-1 unique-marker
   byte-rung directory-entry maintenance facts -- Lean 4 mirror of
   ../rocq/DirBlitMarkerAt.v:
     UnixFs.Dir.dir_blit_marker_at_intro
     UnixFs.Dir.dir_blit_marker_at_value_inode
     UnixFs.Dir.dir_blit_marker_at_value_name
     UnixFs.Dir.dir_blit_marker_at_frame_only

   CONTEXT (test-supervise-sl, 2026-06-19): the landed block-5 marker family
   (0716 DirBlitMarker.lean) is HARDCODED to block 5 (self.dir); _write_entry
   mutates self.disk at an ARBITRARY block `block_num`, so it needs the marker
   generalised over the mutated block. This file is the block-5 family with the
   constant 5 replaced by a variable `blk` everywhere it is the mutated block;
   the block-5 theorems are the blk := 5 instances. SCOPE: VALUE (inode + name)
   + FRAME only -- _write_entry does NOT maintain the block-5 uniq/slots_lt32
   invariants, so no block-parameterized `insert`.

   Faithful interpretation IDENTICAL to DirBlitMarker.lean for the shared symbols.

   Verified under Lean 4 (core only, no Mathlib). No sorry. -/

namespace UnixFs
namespace Dir
section MarkerAt

variable {Disk : Type}
variable (rd : Disk → Int → Int)
variable {Name : Type}
variable (nchar : Name → Int → Int)
variable (nlen : Name → Int)

def slot_off (blk k : Int) : Int := blk * 512 + 32 * k

def slot_inode (d : Disk) (blk k : Int) : Int :=
  256 * rd d (slot_off blk k) + rd d (slot_off blk k + 1)

def scan (rdf : Int → Int) (off : Int) : Nat → List Int
  | 0 => []
  | Nat.succ m => if rdf off = 0 then [] else rdf off :: scan rdf (off + 1) m

def field_to_str (rdf : Int → Int) (off width : Int) : List Int :=
  scan rdf off width.toNat

def slot_name (d : Disk) (blk k : Int) : List Int :=
  field_to_str (rd d) (slot_off blk k + 2) 30

def name_list (nm : Name) : Nat → Int → List Int
  | 0, _ => []
  | Nat.succ m, i => nchar nm i :: name_list nm m (i + 1)

def name_val (nm : Name) : List Int := name_list nchar nm (nlen nm).toNat 0

/-- THE BLOCK-PARAMETERIZED MARKER: the conservative DEFINITION of the abstract
    WhyML predicate, generalised over the mutated block `blk`. -/
def dir_blit_marker_at (d0 d1 : Disk) (blk s b0 b1 : Int) (nm : Name) : Prop :=
  0 ≤ nlen nm
  ∧ nlen nm ≤ 30
  ∧ rd d1 (slot_off blk s) = b0
  ∧ rd d1 (slot_off blk s + 1) = b1
  ∧ (∀ i : Int, 0 ≤ i → i < nlen nm → nchar nm i ≠ 0)
  ∧ (∀ i : Int, 0 ≤ i → i < nlen nm → rd d1 (slot_off blk s + 2 + i) = nchar nm i)
  ∧ (nlen nm < 30 → rd d1 (slot_off blk s + 2 + nlen nm) = 0)
  ∧ (∀ b : Int, 0 ≤ b → b < 512 →
        (b < 32 * s ∨ 32 * s + 32 ≤ b) →
        rd d1 (blk * 512 + b) = rd d0 (blk * 512 + b))

theorem scan_frame (rd0 rd1 : Int → Int) :
    ∀ (fuel : Nat) (off : Int),
      (∀ j, j < fuel → rd0 (off + (j : Int)) = rd1 (off + (j : Int))) →
      scan rd0 off fuel = scan rd1 off fuel := by
  intro fuel
  induction fuel with
  | zero => intro off _; rfl
  | succ m ih =>
    intro off hagree
    have hhead : rd0 off = rd1 off := by
      have h := hagree 0 (by omega); simpa using h
    have htail : scan rd0 (off + 1) m = scan rd1 (off + 1) m := by
      apply ih (off + 1)
      intro j hj
      have h := hagree (j + 1) (by omega)
      have hcast : off + ((j : Int) + 1) = off + 1 + (j : Int) := by omega
      push_cast at h; rw [hcast] at h; exact h
    simp only [scan, hhead, htail]

theorem field_to_str_frame
    (rd0 rd1 : Int → Int) (off width : Int)
    (_hw : 0 ≤ width)
    (hagree : ∀ i : Int, 0 ≤ i → i < width → rd0 (off + i) = rd1 (off + i)) :
    field_to_str rd0 off width = field_to_str rd1 off width := by
  unfold field_to_str
  apply scan_frame rd0 rd1 width.toNat off
  intro j hj
  have hjw : (j : Int) < width := by
    have : ((width.toNat : Int)) = width := Int.toNat_of_nonneg _hw
    omega
  have h := hagree (j : Int) (by omega) hjw
  simpa using h

theorem slot_frame_of_region_at (d0 d1 : Disk) (blk s : Int)
    (hs0 : 0 ≤ s) (hs1 : s < 16)
    (hframe : ∀ b : Int, 0 ≤ b → b < 512 →
        (b < 32 * s ∨ 32 * s + 32 ≤ b) →
        rd d1 (blk * 512 + b) = rd d0 (blk * 512 + b)) :
    ∀ k : Int, 0 ≤ k → k < 16 → k ≠ s →
      slot_inode rd d1 blk k = slot_inode rd d0 blk k ∧
      slot_name rd d1 blk k = slot_name rd d0 blk k := by
  have hslotbytes : ∀ k : Int, 0 ≤ k → k < 16 → k ≠ s →
      ∀ j : Int, 0 ≤ j → j < 32 →
        rd d1 (slot_off blk k + j) = rd d0 (slot_off blk k + j) := by
    intro k hk0 hk1 hne j hj0 hj1
    have hbeq : slot_off blk k + j = blk * 512 + (32 * k + j) := by unfold slot_off; omega
    rw [hbeq]
    apply hframe
    · omega
    · omega
    · omega
  intro k hk0 hk1 hne
  refine ⟨?_, ?_⟩
  · unfold slot_inode
    have hb0 := hslotbytes k hk0 hk1 hne 0 (by omega) (by omega)
    have hb1 := hslotbytes k hk0 hk1 hne 1 (by omega) (by omega)
    simp only [Int.add_zero] at hb0
    rw [hb0, hb1]
  · unfold slot_name
    apply field_to_str_frame (rd d1) (rd d0) (slot_off blk k + 2) 30 (by omega)
    intro i hi0 hi1
    have hcast : slot_off blk k + 2 + i = slot_off blk k + (2 + i) := by omega
    rw [hcast]
    exact hslotbytes k hk0 hk1 hne (2 + i) (by omega) (by omega)

theorem scan_recovers (rdf : Int → Int) (nm : Name) :
    ∀ (fuel : Nat) (off i : Int),
      0 ≤ i →
      i + (fuel : Int) = 30 →
      nlen nm ≤ 30 →
      i ≤ nlen nm →
      (∀ t, i ≤ t → t < nlen nm → nchar nm t ≠ 0) →
      (∀ t, i ≤ t → t < nlen nm → rdf (off + (t - i)) = nchar nm t) →
      (nlen nm < 30 → rdf (off + (nlen nm - i)) = 0) →
      scan rdf off fuel = name_list nchar nm (nlen nm - i).toNat i := by
  intro fuel
  induction fuel with
  | zero =>
    intro off i _ hwf _ hile _ _ _
    have h0 : nlen nm - i = 0 := by simp at hwf; omega
    rw [h0]; simp [scan, name_list]
  | succ m ih =>
    intro off i hi hwf hl30 hile hnn hbytes hnull
    by_cases hlt : i < nlen nm
    · have hb : rdf off = nchar nm i := by
        have h := hbytes i (by omega) hlt
        have : off + (i - i) = off := by omega
        rw [this] at h; exact h
      have hnz : nchar nm i ≠ 0 := hnn i (by omega) hlt
      have hstep : (nlen nm - i).toNat = Nat.succ (nlen nm - (i + 1)).toNat := by omega
      rw [hstep]
      simp only [scan, hb, name_list, if_neg hnz]
      congr 1
      apply ih (off + 1) (i + 1)
      · omega
      · push_cast; omega
      · omega
      · omega
      · intro t ht0 ht1; exact hnn t (by omega) ht1
      · intro t ht0 ht1
        have h := hbytes t (by omega) ht1
        have hc : off + (t - i) = off + 1 + (t - (i + 1)) := by omega
        rw [hc] at h; exact h
      · intro hlt2
        have h := hnull hlt2
        have hc : off + (nlen nm - i) = off + 1 + (nlen nm - (i + 1)) := by omega
        rw [hc] at h; exact h
    · have hieq : i = nlen nm := by omega
      have hlen_lt : nlen nm < 30 := by omega
      have hzero : rdf off = 0 := by
        have h := hnull hlen_lt
        rw [← hieq] at h
        have : off + (i - i) = off := by omega
        rw [this] at h; exact h
      have h0 : nlen nm - i = 0 := by omega
      rw [h0]
      simp [scan, name_list, hzero]

theorem name_round_trip_at (d : Disk) (nm : Name) (blk s : Int)
    (hlen0 : 0 ≤ nlen nm) (hlen30 : nlen nm ≤ 30)
    (hnn : ∀ i, 0 ≤ i → i < nlen nm → nchar nm i ≠ 0)
    (hbytes : ∀ i, 0 ≤ i → i < nlen nm → rd d (slot_off blk s + 2 + i) = nchar nm i)
    (hnull : nlen nm < 30 → rd d (slot_off blk s + 2 + nlen nm) = 0) :
    slot_name rd d blk s = name_val nchar nlen nm := by
  unfold slot_name field_to_str name_val
  have h30 : (30 : Int).toNat = 30 := by decide
  rw [h30]
  have hwf : (0 : Int) + ((30 : Nat) : Int) = 30 := by simp
  have hbytes' : ∀ t : Int, 0 ≤ t → t < nlen nm →
      rd d (slot_off blk s + 2 + (t - 0)) = nchar nm t := by
    intro t ht0 ht1
    have h := hbytes t ht0 ht1
    have he : slot_off blk s + 2 + (t - 0) = slot_off blk s + 2 + t := by omega
    rw [he]; exact h
  have hnull' : nlen nm < 30 → rd d (slot_off blk s + 2 + (nlen nm - 0)) = 0 := by
    intro hlt
    have h := hnull hlt
    have he : slot_off blk s + 2 + (nlen nm - 0) = slot_off blk s + 2 + nlen nm := by omega
    rw [he]; exact h
  have hrec := scan_recovers (nchar := nchar) (nlen := nlen) (rd d) nm 30
    (slot_off blk s + 2) 0
    (by omega) hwf hlen30 (by omega) hnn hbytes' hnull'
  have hz : (nlen nm - 0).toNat = (nlen nm).toNat := by congr 1; omega
  rw [hrec, hz]

/-- dir_blit_marker_at_intro: byte facts -> marker (DEFINITIONAL, zero trust). -/
theorem dir_blit_marker_at_intro (d0 d1 : Disk) (blk s b0 b1 : Int) (nm : Name)
    (hl0 : 0 ≤ nlen nm) (hl30 : nlen nm ≤ 30)
    (hb0 : rd d1 (slot_off blk s) = b0)
    (hb1 : rd d1 (slot_off blk s + 1) = b1)
    (hnn : ∀ i : Int, 0 ≤ i → i < nlen nm → nchar nm i ≠ 0)
    (hbytes : ∀ i : Int, 0 ≤ i → i < nlen nm → rd d1 (slot_off blk s + 2 + i) = nchar nm i)
    (hnull : nlen nm < 30 → rd d1 (slot_off blk s + 2 + nlen nm) = 0)
    (hframe : ∀ b : Int, 0 ≤ b → b < 512 →
        (b < 32 * s ∨ 32 * s + 32 ≤ b) →
        rd d1 (blk * 512 + b) = rd d0 (blk * 512 + b)) :
    dir_blit_marker_at rd nchar nlen d0 d1 blk s b0 b1 nm :=
  ⟨hl0, hl30, hb0, hb1, hnn, hbytes, hnull, hframe⟩

/-- dir_blit_marker_at_value_inode: slot_inode d1 blk s = 256*b0+b1. -/
theorem dir_blit_marker_at_value_inode (d0 d1 : Disk) (blk s b0 b1 : Int) (nm : Name)
    (hmark : dir_blit_marker_at rd nchar nlen d0 d1 blk s b0 b1 nm) :
    slot_inode rd d1 blk s = 256 * b0 + b1 := by
  obtain ⟨_, _, hb0, hb1, _, _, _, _⟩ := hmark
  unfold slot_inode
  rw [hb0, hb1]

/-- dir_blit_marker_at_value_name: slot_name d1 blk s = name_val nm (byte round-trip). -/
theorem dir_blit_marker_at_value_name (d0 d1 : Disk) (blk s b0 b1 : Int) (nm : Name)
    (hmark : dir_blit_marker_at rd nchar nlen d0 d1 blk s b0 b1 nm) :
    slot_name rd d1 blk s = name_val nchar nlen nm := by
  obtain ⟨hnl0, hnl30, _, _, hnn, hbytes, hnull, _⟩ := hmark
  exact name_round_trip_at rd nchar nlen d1 nm blk s hnl0 hnl30 hnn hbytes hnull

/-- dir_blit_marker_at_frame_only: every slot k ≠ s decodes identically in d1, d0. -/
theorem dir_blit_marker_at_frame_only (d0 d1 : Disk) (blk s b0 b1 : Int) (nm : Name)
    (hmark : dir_blit_marker_at rd nchar nlen d0 d1 blk s b0 b1 nm)
    (hs0 : 0 ≤ s) (hs1 : s < 16) :
    ∀ k : Int, 0 ≤ k → k < 16 → k ≠ s →
      slot_inode rd d1 blk k = slot_inode rd d0 blk k ∧
      slot_name rd d1 blk k = slot_name rd d0 blk k := by
  obtain ⟨_, _, _, _, _, _, _, hframe⟩ := hmark
  exact slot_frame_of_region_at rd d0 d1 blk s hs0 hs1 hframe

#print axioms dir_blit_marker_at_intro
#print axioms dir_blit_marker_at_value_inode
#print axioms dir_blit_marker_at_value_name
#print axioms dir_blit_marker_at_frame_only

end MarkerAt
end Dir
end UnixFs
