import Lake
open Lake DSL

/-
  Per-test Lake package for the 0342 GCD cross-validated proofs.

  Provides a project descriptor so that `lake build` and
  `lake env lean --run …` can resolve `import Gcd` from the
  meta-extraction script
  (bin/proof2why3-lean-extract.lean — sticky-02.md Phase B).

  Mathlib is NOT required: the gcd-family theorems use only core
  `Nat.gcd_*` lemmas (`Nat.zero_le`, `Nat.gcd_pos_of_pos_left`,
  `Nat.mod_eq_zero_of_dvd`, `Nat.gcd_dvd_left`, `Nat.gcd_zero_right`,
  `Nat.gcd_rec`, `Nat.gcd_comm`, `Nat.dvd_of_mod_eq_zero`,
  `Nat.dvd_gcd`, `Nat.le_of_dvd`, `Nat.gcd_pos_of_pos_right`).
-/

package PycslReferenceGcd0342 where
  leanOptions := #[⟨`autoImplicit, false⟩]

@[default_target]
lean_lib PycslReferenceGcd0342 where
  srcDir := "."
  roots := #[`Gcd]
