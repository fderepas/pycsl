-- Cross-validated Lean proofs for test-suite/corpus/pycsl-reference/0753.py
-- #@ proof lean Pycsl.Struct.Std.{round_trip_u16,round_trip_u32}
-- Core Lean 4 (no Mathlib); Int `/`,`%` are Euclidean for positive divisor,
-- matching Why3 int.EuclideanDivision. pack/unpack are DEFINED as the real
-- big-endian base-256 byte serialisation (with struct's mod-256 truncation),
-- so the guarded round-trip is a genuine theorem. No sorry / axioms.

namespace Pycsl.Struct.Std

-- ---- uint16, big-endian '>H' ----
def pack16 (x : Int) : List Int := [(x / 256) % 256, x % 256]

def unpack16 : List Int → Int
  | b0 :: b1 :: _ => b0 * 256 + b1
  | _ => 0

theorem size_u16 (x : Int) : (pack16 x).length = 2 := rfl

theorem round_trip_u16 (x : Int) (h0 : 0 ≤ x) (h1 : x < 65536) :
    unpack16 (pack16 x) = x := by
  show ((x / 256) % 256) * 256 + x % 256 = x
  have hmod := Int.emod_add_mul_ediv x 256
  have hr0 : 0 ≤ x % 256 := Int.emod_nonneg x (by omega)
  have hr1 : x % 256 < 256 := Int.emod_lt_of_pos x (by omega)
  have hq0 : 0 ≤ x / 256 := Int.ediv_nonneg h0 (by omega)
  have hqlt : x / 256 < 256 := by omega
  have hz : (x / 256) / 256 = 0 := Int.ediv_eq_zero_of_lt hq0 hqlt
  have hqm := Int.emod_add_mul_ediv (x / 256) 256
  rw [hz] at hqm
  omega

theorem guard_necessity_u16 : unpack16 (pack16 65536) = 0 ∧ (65536 : Int) ≠ 0 := by
  decide

-- ---- uint32, big-endian '>I' ----
def pack32 (x : Int) : List Int :=
  [(x / 16777216) % 256, (x / 65536) % 256, (x / 256) % 256, x % 256]

def unpack32 : List Int → Int
  | b0 :: b1 :: b2 :: b3 :: _ => b0 * 16777216 + b1 * 65536 + b2 * 256 + b3
  | _ => 0

theorem size_u32 (x : Int) : (pack32 x).length = 4 := rfl

theorem round_trip_u32 (x : Int) (h0 : 0 ≤ x) (h1 : x < 4294967296) :
    unpack32 (pack32 x) = x := by
  show ((x / 16777216) % 256) * 16777216 + ((x / 65536) % 256) * 65536
       + ((x / 256) % 256) * 256 + x % 256 = x
  -- telescoping base-256 quotients: x/256/256 = x/65536, x/65536/256 = x/16777216
  have tA : x / 256 / 256 = x / 65536 := by
    rw [Int.ediv_ediv_of_nonneg (by omega : (0:Int) ≤ 256)]; omega
  have tB : x / 65536 / 256 = x / 16777216 := by
    rw [Int.ediv_ediv_of_nonneg (by omega : (0:Int) ≤ 65536)]; omega
  have m0 := Int.emod_add_mul_ediv x 256
  have m1 := Int.emod_add_mul_ediv (x / 256) 256
  have m2 := Int.emod_add_mul_ediv (x / 65536) 256
  rw [tA] at m1
  rw [tB] at m2
  have r0 : 0 ≤ x % 256 := Int.emod_nonneg x (by omega)
  have r1 : x % 256 < 256 := Int.emod_lt_of_pos x (by omega)
  have s0 : 0 ≤ (x / 256) % 256 := Int.emod_nonneg _ (by omega)
  have s1 : (x / 256) % 256 < 256 := Int.emod_lt_of_pos _ (by omega)
  have t0 : 0 ≤ (x / 65536) % 256 := Int.emod_nonneg _ (by omega)
  have t1 : (x / 65536) % 256 < 256 := Int.emod_lt_of_pos _ (by omega)
  have hh0 : 0 ≤ x / 16777216 := Int.ediv_nonneg h0 (by omega)
  have hhlt : x / 16777216 < 256 := by omega
  have hz : (x / 16777216) / 256 = 0 := Int.ediv_eq_zero_of_lt hh0 hhlt
  have m3 := Int.emod_add_mul_ediv (x / 16777216) 256
  rw [hz] at m3
  omega

theorem guard_necessity_u32 : unpack32 (pack32 4294967296) = 0 ∧ (4294967296 : Int) ≠ 0 := by
  decide

end Pycsl.Struct.Std
