/- Validation of UnixFs.Field.field_to_str_frame (string-codec Phase A',
   DISJOINT-REGION FRAME) -- Lean 4 mirror of ../rocq/FieldToStrFrame.v.

   The byte-locality twin of field_to_str_round_trip. The Why3 axiom constrains
   an ABSTRACT `field_to_str : array int -> int -> int -> string`; this file
   exhibits the SAME concrete scan-to-first-null decode as FieldToStrRoundTrip
   and proves the frame over it, witnessing the axiom's consistency.

   The frame: the decode of a `width`-byte null-padded field at `off` depends
   ONLY on the bytes d[off..off+width). If two disks d0, d1 agree byte-for-byte
   over that window, they decode to the SAME name. This is the disjoint-region
   twin of the retired block5_decode_frame (full block agreement); a blit on one
   slot leaves every OTHER slot's name window untouched.

   Faithful interpretation of the Why3 symbols (IDENTICAL to FieldToStrRoundTrip):
     - Why3 `string`              <-> `List Int`.
     - `array int` read `d[b]`    <-> abstract byte reader `rd : Int -> Int`.
     - `field_to_str d off width` <-> `scan rd off width.toNat`.
     - string equality `=`        <-> List equality.

   Two disks are modelled by two abstract byte readers rd0, rd1; the byte-frame
   antecedent becomes `forall i. 0 <= i < width -> rd0 (off+i) = rd1 (off+i)`.

   Verified under Lean 4.30.0 (core only, no Mathlib). No sorry. -/

namespace UnixFs
namespace Field
section Frame

/-- The concrete decode: read up to `fuel` bytes from `off`, stopping at the
    first null byte (the SAME scan as FieldToStrRoundTrip.lean). -/
def scan (rd : Int → Int) (off : Int) : Nat → List Int
  | 0 => []
  | Nat.succ m => if rd off = 0 then [] else rd off :: scan rd (off + 1) m

def field_to_str (rd : Int → Int) (off width : Int) : List Int :=
  scan rd off width.toNat

/-- Core induction: if rd0 and rd1 agree on every offset the scan reads within
    `fuel` bytes from `off`, the two scans are equal. -/
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
      have h := hagree 0 (by omega)
      simpa using h
    have htail : scan rd0 (off + 1) m = scan rd1 (off + 1) m := by
      apply ih (off + 1)
      intro j hj
      have h := hagree (j + 1) (by omega)
      have hcast : off + ((j : Int) + 1) = off + 1 + (j : Int) := by omega
      push_cast at h
      rw [hcast] at h
      exact h
    simp only [scan, hhead, htail]

/-- The frame, mirroring the Why3 axiom: `width : Int` with `0 ≤ width`; the
    byte-agreement hypothesis over the int index set `0 ≤ i < width`. -/
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

#print axioms field_to_str_frame

end Frame
end Field
end UnixFs
