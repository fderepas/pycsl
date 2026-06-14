/- Validation of UnixFs.Field.field_to_str_round_trip (string-codec Phase A') --
   Lean 4 mirror of ../rocq/FieldToStrRoundTrip.v.

   The string <-> fixed-width null-padded byte-field codec ROUND-TRIP. The Why3
   axiom constrains an ABSTRACT `field_to_str : array int -> int -> int -> string`;
   this file exhibits the concrete scan-to-first-null decode and proves the
   round-trip over it, witnessing the axiom's consistency (as Block5DecodeFrame).

   Faithful interpretation of the Why3 symbols:
     - Why3 `string`              <-> `List Int` (a char is its code).
     - `String.length name`       <-> `(name.length : Int)`.
     - `Char.code (Char.get name i)` <-> `name.getD i.toNat 0`.
     - `array int` read `d[b]`    <-> abstract byte reader `rd : Int -> Int`.
     - `field_to_str d off width` <-> `scan rd off width.toNat` (bytes up to the
                                       first null, Python '>Ns').
     - string equality `=`        <-> List equality (Why3 string extensionality
                                       IS structural list equality -- free here
                                       by induction, where SMT E-match-explodes).

   Verified under Lean 4.30.0 (core only, no Mathlib). No sorry. -/

namespace UnixFs
namespace Field
section Codec

/-- The concrete decode: read up to `fuel` bytes from `off`, stopping at the
    first null byte. Faithful model of the Python '>Ns' field decode. -/
def scan (rd : Int → Int) (off : Int) : Nat → List Int
  | 0 => []
  | Nat.succ m => if rd off = 0 then [] else rd off :: scan rd (off + 1) m

def field_to_str (rd : Int → Int) (off width : Int) : List Int :=
  scan rd off width.toNat

/-- Core induction: the scan recovers `name` exactly when, within `fuel` bytes,
    every name byte is present, none is null, and (if there is room) a null
    terminator follows. -/
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

/-- The round-trip, mirroring the Why3 axiom: `width : Int` with
    `0 ≤ length name ≤ width`; hypotheses over the int index set
    `0 ≤ i < length name`. -/
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
  · -- length name ≤ width.toNat
    have : (name.length : Int) ≤ (width.toNat : Int) := by
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

#print axioms field_to_str_round_trip

end Codec
end Field
end UnixFs
