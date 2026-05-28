-- test-suite/corpus/pycsl-reference/0342.proofs/lean/Gcd.lean
--
-- Lean proofs of the Euclidean GCD postconditions stated in 0342.py.
-- Referenced by `#@ proof lean: Pycsl.Reference.Gcd.<thm>` directives.
--
-- Verified under Lean 4.29.1. The proofs use core `Nat.gcd` lemmas —
-- no sorry, no axioms.

namespace Pycsl.Reference.Gcd

/-- `\result >= 0` — `Nat.gcd` returns a `Nat`. -/
theorem gcd_result_nonneg (a b : Nat) : Nat.gcd a b ≥ 0 :=
  Nat.zero_le _

/-- `(a > 0 ∨ b > 0) → \result > 0`. -/
theorem gcd_result_positive (a b : Nat) (h : a > 0 ∨ b > 0) :
    Nat.gcd a b > 0 := by
  rcases h with ha | hb
  · exact Nat.gcd_pos_of_pos_left b ha
  · exact Nat.gcd_pos_of_pos_right a hb

/-- `(a > 0 ∨ b > 0) → a % \result = 0`. -/
theorem gcd_divides_a (a b : Nat) (_h : a > 0 ∨ b > 0) :
    a % Nat.gcd a b = 0 :=
  Nat.mod_eq_zero_of_dvd (Nat.gcd_dvd_left a b)

/-- `(a > 0 ∨ b > 0) → b % \result = 0`. -/
theorem gcd_divides_b (a b : Nat) (_h : a > 0 ∨ b > 0) :
    b % Nat.gcd a b = 0 :=
  Nat.mod_eq_zero_of_dvd (Nat.gcd_dvd_right a b)

/-- Loop-exit collapse: `gcd a 0 = a`. Matches the WhyML axiom `gcd_0`,
    which lets the loop invariant `gcd(x, y) == gcd(a, b)` discharge
    the postcondition once `y` reaches 0. -/
theorem gcd_0 (a : Nat) : Nat.gcd a 0 = a :=
  Nat.gcd_zero_right a

/-- Euclidean step: `gcd a b = gcd b (a mod b)` when `b > 0`. Matches the
    WhyML axiom `gcd_step`, the load-bearing invariant-preservation lemma
    for the Euclidean loop body. -/
theorem gcd_step (a b : Nat) (_h : b > 0) :
    Nat.gcd a b = Nat.gcd b (a % b) := by
  rw [Nat.gcd_comm a b, Nat.gcd_rec b a, Nat.gcd_comm]

/-- Maximality: any positive common divisor `k` of `a` and `b` is at most
    `Nat.gcd a b`. This is the load-bearing axiom that turns the contract
    from "result is *a* common divisor" into "result is the *greatest*
    common divisor". Matches the WhyML axiom `gcd_greatest`. -/
theorem gcd_greatest (a b k : Nat) (hpos : a > 0 ∨ b > 0)
    (_hk : k > 0) (ha : a % k = 0) (hb : b % k = 0) :
    k ≤ Nat.gcd a b := by
  have ha' : k ∣ a := Nat.dvd_of_mod_eq_zero ha
  have hb' : k ∣ b := Nat.dvd_of_mod_eq_zero hb
  have hd : k ∣ Nat.gcd a b := Nat.dvd_gcd ha' hb'
  have hgpos : 0 < Nat.gcd a b := by
    rcases hpos with hA | hB
    · exact Nat.gcd_pos_of_pos_left b hA
    · exact Nat.gcd_pos_of_pos_right a hB
  exact Nat.le_of_dvd hgpos hd

end Pycsl.Reference.Gcd
