-- Cross-validated Lean proofs for src/pycsl_lib/csys/__init__.py
-- #@ proof lean Pycsl.Csys.Colorsys.{sat_bound,hue_bound}
-- Core Lean 4 (no Mathlib); Int `/` is Euclidean for positive divisor,
-- matching Why3 int.EuclideanDivision. No sorry / axioms.

namespace Pycsl.Csys.Colorsys

theorem sat_bound (d m : Int) (_hd : 0 ≤ d) (hdm : d ≤ m) (hm : m > 0) :
    (d * 1000) / m ≤ 1000 := by
  have hmod := Int.emod_add_ediv (d * 1000) m
  have hr0 : 0 ≤ (d * 1000) % m := Int.emod_nonneg _ (by omega)
  have hmq : m * ((d * 1000) / m) ≤ m * 1000 := by omega
  exact Int.le_of_mul_le_mul_left hmq hm

theorem hue_bound (n d : Int) (hd : d > 0) (hlo : (0 - d) ≤ n) (hhi : n ≤ d) :
    (0 - 167) ≤ (n * 1000) / (6 * d) ∧ (n * 1000) / (6 * d) ≤ 167 := by
  have hne : (6 * d) ≠ 0 := by omega
  have hub : (1000 * d) / (6 * d) = 166 := by
    have e : 1000 * d = 4 * d + 166 * (6 * d) := by omega
    have hz : (4 * d) / (6 * d) = 0 := Int.ediv_eq_zero_of_lt (by omega) (by omega)
    rw [e, Int.add_mul_ediv_right _ _ hne]; omega
  have hlb : (0 - 1000 * d) / (6 * d) = -167 := by
    have e : 0 - 1000 * d = 2 * d + (-167) * (6 * d) := by omega
    have hz : (2 * d) / (6 * d) = 0 := Int.ediv_eq_zero_of_lt (by omega) (by omega)
    rw [e, Int.add_mul_ediv_right _ _ hne]; omega
  refine ⟨?_, ?_⟩
  · calc (0 - 167 : Int) = (0 - 1000 * d) / (6 * d) := hlb.symm
      _ ≤ (n * 1000) / (6 * d) := Int.ediv_le_ediv (by omega) (by omega)
  · calc (n * 1000) / (6 * d) ≤ (1000 * d) / (6 * d) := Int.ediv_le_ediv (by omega) (by omega)
      _ = 166 := hub
      _ ≤ 167 := by omega

end Pycsl.Csys.Colorsys
