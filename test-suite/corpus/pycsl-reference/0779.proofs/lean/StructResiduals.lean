-- cleared-pack RESIDUALS — cross-validated Lean proofs for the faithful struct
-- family widened to a per-field width/signedness tag: multi-slot unsigned
-- (u16u32), signed singles (i16/i32/i64, two's complement), signed multi
-- (i32i32), and fixed-bytes (s4).  Core Lean 4 (no Mathlib); Int `/`,`%` are
-- Euclidean for a positive divisor, matching Why3 int.EuclideanDivision.
-- pack/unpack are DEFINED as the real big-endian base-256 byte serialisation
-- (with struct's mod-256 truncation and two's-complement folding), so every
-- round-trip is a genuine theorem. No sorry / no extra axioms.

namespace Pycsl.Struct.Std

-- ===== unsigned single-field big-endian base-256 codecs =====
def pk16 (x : Int) : List Int := [(x / 256) % 256, x % 256]
def up16 : List Int → Int
  | b0 :: b1 :: _ => b0 * 256 + b1
  | _ => 0

def pk32 (x : Int) : List Int :=
  [(x / 16777216) % 256, (x / 65536) % 256, (x / 256) % 256, x % 256]
def up32 : List Int → Int
  | b0 :: b1 :: b2 :: b3 :: _ => b0 * 16777216 + b1 * 65536 + b2 * 256 + b3
  | _ => 0

def pk64 (x : Int) : List Int :=
  [(x / 72057594037927936) % 256, (x / 281474976710656) % 256,
   (x / 1099511627776) % 256, (x / 4294967296) % 256,
   (x / 16777216) % 256, (x / 65536) % 256, (x / 256) % 256, x % 256]
def up64 : List Int → Int
  | b0 :: b1 :: b2 :: b3 :: b4 :: b5 :: b6 :: b7 :: _ =>
      b0 * 72057594037927936 + b1 * 281474976710656 + b2 * 1099511627776 +
      b3 * 4294967296 + b4 * 16777216 + b5 * 65536 + b6 * 256 + b7
  | _ => 0

theorem urt16 (x : Int) (h0 : 0 ≤ x) (h1 : x < 65536) : up16 (pk16 x) = x := by
  show ((x / 256) % 256) * 256 + x % 256 = x
  have hr0 : 0 ≤ x % 256 := Int.emod_nonneg x (by omega)
  have hr1 : x % 256 < 256 := Int.emod_lt_of_pos x (by omega)
  have hq0 : 0 ≤ x / 256 := Int.ediv_nonneg h0 (by omega)
  have hqlt : x / 256 < 256 := by omega
  have hz : (x / 256) / 256 = 0 := Int.ediv_eq_zero_of_lt hq0 hqlt
  have hqm := Int.emod_add_mul_ediv (x / 256) 256
  have hm := Int.emod_add_mul_ediv x 256
  rw [hz] at hqm
  omega

theorem urt32 (x : Int) (h0 : 0 ≤ x) (h1 : x < 4294967296) : up32 (pk32 x) = x := by
  show ((x / 16777216) % 256) * 16777216 + ((x / 65536) % 256) * 65536
       + ((x / 256) % 256) * 256 + x % 256 = x
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

theorem urt64 (x : Int) (h0 : 0 ≤ x) (h1 : x < 18446744073709551616) : up64 (pk64 x) = x := by
  show ((x / 72057594037927936) % 256) * 72057594037927936
       + ((x / 281474976710656) % 256) * 281474976710656
       + ((x / 1099511627776) % 256) * 1099511627776
       + ((x / 4294967296) % 256) * 4294967296
       + ((x / 16777216) % 256) * 16777216
       + ((x / 65536) % 256) * 65536
       + ((x / 256) % 256) * 256 + x % 256 = x
  have tA : x / 256 / 256 = x / 65536 := by
    rw [Int.ediv_ediv_of_nonneg (by omega : (0:Int) ≤ 256)]; omega
  have tB : x / 65536 / 256 = x / 16777216 := by
    rw [Int.ediv_ediv_of_nonneg (by omega : (0:Int) ≤ 65536)]; omega
  have tC : x / 16777216 / 256 = x / 4294967296 := by
    rw [Int.ediv_ediv_of_nonneg (by omega : (0:Int) ≤ 16777216)]; omega
  have tD : x / 4294967296 / 256 = x / 1099511627776 := by
    rw [Int.ediv_ediv_of_nonneg (by omega : (0:Int) ≤ 4294967296)]; omega
  have tE : x / 1099511627776 / 256 = x / 281474976710656 := by
    rw [Int.ediv_ediv_of_nonneg (by omega : (0:Int) ≤ 1099511627776)]; omega
  have tF : x / 281474976710656 / 256 = x / 72057594037927936 := by
    rw [Int.ediv_ediv_of_nonneg (by omega : (0:Int) ≤ 281474976710656)]; omega
  have m0 := Int.emod_add_mul_ediv x 256
  have m1 := Int.emod_add_mul_ediv (x / 256) 256
  have m2 := Int.emod_add_mul_ediv (x / 65536) 256
  have m3 := Int.emod_add_mul_ediv (x / 16777216) 256
  have m4 := Int.emod_add_mul_ediv (x / 4294967296) 256
  have m5 := Int.emod_add_mul_ediv (x / 1099511627776) 256
  have m6 := Int.emod_add_mul_ediv (x / 281474976710656) 256
  rw [tA] at m1; rw [tB] at m2; rw [tC] at m3; rw [tD] at m4; rw [tE] at m5; rw [tF] at m6
  have r0 : 0 ≤ x % 256 := Int.emod_nonneg x (by omega)
  have r1 : x % 256 < 256 := Int.emod_lt_of_pos x (by omega)
  have s0 : 0 ≤ (x / 256) % 256 := Int.emod_nonneg _ (by omega)
  have s1 : (x / 256) % 256 < 256 := Int.emod_lt_of_pos _ (by omega)
  have t0 : 0 ≤ (x / 65536) % 256 := Int.emod_nonneg _ (by omega)
  have t1 : (x / 65536) % 256 < 256 := Int.emod_lt_of_pos _ (by omega)
  have u0 : 0 ≤ (x / 16777216) % 256 := Int.emod_nonneg _ (by omega)
  have u1 : (x / 16777216) % 256 < 256 := Int.emod_lt_of_pos _ (by omega)
  have v0 : 0 ≤ (x / 4294967296) % 256 := Int.emod_nonneg _ (by omega)
  have v1 : (x / 4294967296) % 256 < 256 := Int.emod_lt_of_pos _ (by omega)
  have w0 : 0 ≤ (x / 1099511627776) % 256 := Int.emod_nonneg _ (by omega)
  have w1 : (x / 1099511627776) % 256 < 256 := Int.emod_lt_of_pos _ (by omega)
  have y0 : 0 ≤ (x / 281474976710656) % 256 := Int.emod_nonneg _ (by omega)
  have y1 : (x / 281474976710656) % 256 < 256 := Int.emod_lt_of_pos _ (by omega)
  have hh0 : 0 ≤ x / 72057594037927936 := Int.ediv_nonneg h0 (by omega)
  have hhlt : x / 72057594037927936 < 256 := by omega
  have hz : (x / 72057594037927936) / 256 = 0 := Int.ediv_eq_zero_of_lt hh0 hhlt
  have m7 := Int.emod_add_mul_ediv (x / 72057594037927936) 256
  rw [hz] at m7
  omega

-- ===== signed single-field codecs (two's complement) =====
def pk_i16 (x : Int) : List Int := pk16 (x % 65536)
def up_i16 (d : List Int) : Int := let u := up16 d; if 32768 ≤ u then u - 65536 else u
def pk_i32 (x : Int) : List Int := pk32 (x % 4294967296)
def up_i32 (d : List Int) : Int := let u := up32 d; if 2147483648 ≤ u then u - 4294967296 else u
def pk_i64 (x : Int) : List Int := pk64 (x % 18446744073709551616)
def up_i64 (d : List Int) : Int :=
  let u := up64 d; if 9223372036854775808 ≤ u then u - 18446744073709551616 else u

theorem srt16 (x : Int) (h0 : -32768 ≤ x) (h1 : x < 32768) : up_i16 (pk_i16 x) = x := by
  unfold up_i16 pk_i16
  have hm0 : 0 ≤ x % 65536 := Int.emod_nonneg x (by omega)
  have hm1 : x % 65536 < 65536 := Int.emod_lt_of_pos x (by omega)
  rw [urt16 (x % 65536) hm0 hm1]
  have e := Int.emod_add_mul_ediv x 65536
  by_cases hc : 32768 ≤ x % 65536
  · simp [hc]; omega
  · simp [hc]; omega

theorem srt32 (x : Int) (h0 : -2147483648 ≤ x) (h1 : x < 2147483648) : up_i32 (pk_i32 x) = x := by
  unfold up_i32 pk_i32
  have hm0 : 0 ≤ x % 4294967296 := Int.emod_nonneg x (by omega)
  have hm1 : x % 4294967296 < 4294967296 := Int.emod_lt_of_pos x (by omega)
  rw [urt32 (x % 4294967296) hm0 hm1]
  have e := Int.emod_add_mul_ediv x 4294967296
  by_cases hc : 2147483648 ≤ x % 4294967296
  · simp [hc]; omega
  · simp [hc]; omega

theorem srt64 (x : Int) (h0 : -9223372036854775808 ≤ x) (h1 : x < 9223372036854775808) :
    up_i64 (pk_i64 x) = x := by
  unfold up_i64 pk_i64
  have hm0 : 0 ≤ x % 18446744073709551616 := Int.emod_nonneg x (by omega)
  have hm1 : x % 18446744073709551616 < 18446744073709551616 := Int.emod_lt_of_pos x (by omega)
  rw [urt64 (x % 18446744073709551616) hm0 hm1]
  have e := Int.emod_add_mul_ediv x 18446744073709551616
  by_cases hc : 9223372036854775808 ≤ x % 18446744073709551616
  · simp [hc]; omega
  · simp [hc]; omega

-- ===== multi-slot: fields occupy disjoint byte ranges (concatenation) =====
def pk_u16u32 (x0 x1 : Int) : List Int := pk16 x0 ++ pk32 x1
def up_u16u32 : List Int → Int × Int
  | b0 :: b1 :: b2 :: b3 :: b4 :: b5 :: _ =>
      (up16 [b0, b1], up32 [b2, b3, b4, b5])
  | _ => (0, 0)

theorem round_trip_u16u32 (x0 x1 : Int)
    (a0 : 0 ≤ x0) (a1 : x0 < 65536) (b0 : 0 ≤ x1) (b1 : x1 < 4294967296) :
    up_u16u32 (pk_u16u32 x0 x1) = (x0, x1) := by
  show (up16 (pk16 x0), up32 (pk32 x1)) = (x0, x1)
  rw [urt16 x0 a0 a1, urt32 x1 b0 b1]

def pk_i32i32 (x0 x1 : Int) : List Int := pk_i32 x0 ++ pk_i32 x1
def up_i32i32 : List Int → Int × Int
  | b0 :: b1 :: b2 :: b3 :: b4 :: b5 :: b6 :: b7 :: _ =>
      (up_i32 [b0, b1, b2, b3], up_i32 [b4, b5, b6, b7])
  | _ => (0, 0)

theorem round_trip_i32i32 (x0 x1 : Int)
    (a0 : -2147483648 ≤ x0) (a1 : x0 < 2147483648)
    (b0 : -2147483648 ≤ x1) (b1 : x1 < 2147483648) :
    up_i32i32 (pk_i32i32 x0 x1) = (x0, x1) := by
  show (up_i32 (pk_i32 x0), up_i32 (pk_i32 x1)) = (x0, x1)
  rw [srt32 x0 a0 a1, srt32 x1 b0 b1]

-- named single-field round-trips for citation
theorem round_trip_i16 (x : Int) (h0 : -32768 ≤ x) (h1 : x < 32768) :
    up_i16 (pk_i16 x) = x := srt16 x h0 h1
theorem round_trip_i32 (x : Int) (h0 : -2147483648 ≤ x) (h1 : x < 2147483648) :
    up_i32 (pk_i32 x) = x := srt32 x h0 h1
theorem round_trip_i64 (x : Int) (h0 : -9223372036854775808 ≤ x) (h1 : x < 9223372036854775808) :
    up_i64 (pk_i64 x) = x := srt64 x h0 h1

-- ===== fixed-bytes s4: identity under the length guard =====
def pk_s4 (d : List Int) : List Int := d.take 4
def up_s4 (d : List Int) : List Int := d

theorem round_trip_s4 (d : List Int) (h : d.length = 4) : up_s4 (pk_s4 d) = d := by
  unfold up_s4 pk_s4
  apply List.take_of_length_le
  omega

-- ===== size laws =====
theorem size_u16u32 (x0 x1 : Int) : (pk_u16u32 x0 x1).length = 6 := rfl
theorem size_i16 (x : Int) : (pk_i16 x).length = 2 := rfl
theorem size_i32 (x : Int) : (pk_i32 x).length = 4 := rfl
theorem size_i64 (x : Int) : (pk_i64 x).length = 8 := rfl
theorem size_i32i32 (x0 x1 : Int) : (pk_i32i32 x0 x1).length = 8 := rfl

-- ===== guard-necessity counterexamples =====
theorem guard_necessity_u16u32 : up_u16u32 (pk_u16u32 65536 0) = (0, 0) ∧ (65536 : Int) ≠ 0 := by
  decide
theorem guard_necessity_i16 : up_i16 (pk_i16 32768) = -32768 ∧ (32768 : Int) ≠ -32768 := by
  decide

end Pycsl.Struct.Std
