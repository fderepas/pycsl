/- Validation of UnixFs.Dir.slot_name_byte_decode (Gap-5 keystone, STRING half)
   -- Lean 4 mirror of ../rocq/SlotNameByteDecode.v.

   The byte->decode fact for the directory per-slot NAME field, the string twin
   of slot_inode_byte_decode (the inode half).

   A directory slot is 32 bytes (struct '>H30s'): a 2-byte big-endian inode
   field followed by a 30-byte null-padded name field. slot_name blk k is the
   decoded name in the 30-byte field at offset slot_off blk k + 2 -- exactly
   field_to_str (slot_off blk k + 2) 30, the SAME scan-to-first-null '>Ns'
   decode validated in FieldToStrRoundTrip.lean. The WRITE-DIRECTION round-trip:
   if the 30 name-field bytes are byte-for-byte the null-padded encoding of
   `name`, then slot_name blk k = name. This composes the slot offset (+2 past
   the inode field) with the already-cross-validated field_to_str round-trip.

   UNLIKE the inode byte-decode (a finite 2-byte equation SMT applies in O(1)),
   the name decode is by string extensionality over the 30-byte scan, the
   measured ~23M-step Alt-Ergo/Z3 string wall -- so the SAME cited-axiom trust
   class as field_to_str_round_trip: SMT only APPLIES it.

   Faithful interpretation of the Why3 symbols:
     - Why3 `string`              <-> `List Int` (a char is its code).
     - `String.length name`       <-> `(name.length : Int)`.
     - `Char.code (Char.get name i)` <-> `name.getD i.toNat 0`.
     - `array int` read `d[b]`    <-> abstract byte reader `rd : Int -> Int`.
     - `field_to_str d off width` <-> `scan rd off width.toNat`.
     - `slot_name d blk k`        <-> `field_to_str (slot_off blk k + 2) 30`.
     - string equality `=`        <-> List equality (Why3 string extensionality
                                       IS structural list equality, free here).

   Verified under Lean 4 (core only, no Mathlib). No sorry. -/

namespace UnixFs
namespace Dir
section Scan

/-- The field_to_str codec, identical to FieldToStrRoundTrip.lean. -/
def scan (rd : Int → Int) (off : Int) : Nat → List Int
  | 0 => []
  | Nat.succ m => if rd off = 0 then [] else rd off :: scan rd (off + 1) m

def field_to_str (rd : Int → Int) (off width : Int) : List Int :=
  scan rd off width.toNat

theorem scan_round_trip (rd : Int → Int) :
    ∀ (name : List Int) (off : Int) (fuel : Nat),
      name.length ≤ fuel →
      (∀ j, j < name.length → name.getD j 0 ≠ 0) →
      (∀ j, j < name.length → rd (off + (j : Int)) = name.getD j 0) →
      (name.length < fuel → rd (off + (name.length : Int)) = 0) →
      scan rd off fuel = name := by
  intro name
  induction name with
  | nil =>
    intro off fuel _ _ _ hterm
    cases fuel with
    | zero => rfl
    | succ m =>
      have hz : rd off = 0 := by
        have h := hterm (by simp)
        simpa using h
      simp [scan, hz]
  | cons a name' ih =>
    intro off fuel hlen hnn hb hterm
    cases fuel with
    | zero => simp at hlen
    | succ m =>
      have ha : rd off = a := by
        have h := hb 0 (by simp)
        simpa using h
      have ha0 : a ≠ 0 := by
        have h := hnn 0 (by simp)
        simpa using h
      have hcond : ¬ (rd off = 0) := by rw [ha]; exact ha0
      simp only [scan]
      rw [if_neg hcond, ha]
      congr 1
      apply ih (off + 1) m
      · simp only [List.length_cons] at hlen; omega
      · intro j hj
        have h := hnn (j + 1) (by simp only [List.length_cons]; omega)
        simpa using h
      · intro j hj
        have h := hb (j + 1) (by simp only [List.length_cons]; omega)
        simp only [List.getD_cons_succ] at h
        push_cast at h
        have hcast : off + 1 + (j : Int) = off + ((j : Int) + 1) := by omega
        rw [hcast]; exact h
      · intro hlt
        have h := hterm (by simp only [List.length_cons]; omega)
        simp only [List.length_cons] at h
        push_cast at h
        have hcast : off + 1 + (name'.length : Int) = off + ((name'.length : Int) + 1) := by omega
        rw [hcast]; exact h

theorem field_to_str_round_trip
    (rd : Int → Int) (name : List Int) (off width : Int)
    (_h0 : 0 ≤ (name.length : Int))
    (hle : (name.length : Int) ≤ width)
    (hnn : ∀ i : Int, 0 ≤ i → i < (name.length : Int) → name.getD i.toNat 0 ≠ 0)
    (hb : ∀ i : Int, 0 ≤ i → i < (name.length : Int) → rd (off + i) = name.getD i.toNat 0)
    (hterm : (name.length : Int) < width → rd (off + (name.length : Int)) = 0) :
    field_to_str rd off width = name := by
  unfold field_to_str
  apply scan_round_trip rd name off width.toNat
  · have : (name.length : Int) ≤ (width.toNat : Int) := by
      rw [Int.toNat_of_nonneg (by omega)]; exact hle
    omega
  · intro j hj
    have h := hnn (j : Int) (by omega) (by omega)
    simpa using h
  · intro j hj
    have h := hb (j : Int) (by omega) (by omega)
    simpa using h
  · intro hlt
    apply hterm
    have hwnn : 0 ≤ width := by omega
    have : ((width.toNat : Int)) = width := Int.toNat_of_nonneg hwnn
    omega

/-- Slot offset: a slot is 32 bytes, blk is a 512-byte block. -/
def slotOff (blk k : Int) : Int := blk * 512 + 32 * k

/-- slot_name reads the 30-byte name field, starting 2 bytes into the slot
    (after the 2-byte inode field): field_to_str at off + 2, width 30. -/
def slotName (rd : Int → Int) (blk k : Int) : List Int :=
  field_to_str rd (slotOff blk k + 2) 30

/-- WRITE-DIRECTION: if the 30 name-field bytes of slot k are byte-for-byte the
    null-padded encoding of `name`, then slot_name blk k = name. This is
    field_to_str_round_trip specialised to off = slotOff blk k + 2, width = 30. -/
theorem slot_name_byte_decode
    (rd : Int → Int) (name : List Int) (blk k : Int)
    (hle : (name.length : Int) ≤ 30)
    (hnn : ∀ i : Int, 0 ≤ i → i < (name.length : Int) → name.getD i.toNat 0 ≠ 0)
    (hb : ∀ i : Int, 0 ≤ i → i < (name.length : Int) →
        rd (slotOff blk k + 2 + i) = name.getD i.toNat 0)
    (hterm : (name.length : Int) < 30 →
        rd (slotOff blk k + 2 + (name.length : Int)) = 0) :
    slotName rd blk k = name := by
  unfold slotName
  apply field_to_str_round_trip rd name (slotOff blk k + 2) 30
  · omega
  · exact hle
  · exact hnn
  · exact hb
  · exact hterm

#print axioms slot_name_byte_decode

end Scan
end Dir
end UnixFs
