(*
 * Golden test fixture for rocq2pycsl — lists with universal quantification.
 *
 * Exercises `length arr` → IR `Length`, `nth i arr 0` → IR `Nth`, and
 * an inner `forall i : nat, ...` whose `nat` binder picks up the
 * automatic `i >= 0 ==>` guard from the translator.
 *)

Require Import Arith.
Require Import List.

Definition array_sum_nonneg (arr : list nat) (n : nat) : nat := 0. (* trusted oracle *)

Theorem array_sum_nonneg_nonneg :
  forall (arr : list nat) (n : nat),
    n <= length arr ->
    array_sum_nonneg arr n >= 0.
Admitted.
