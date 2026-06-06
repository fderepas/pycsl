(*
 * Golden test fixture for rocq2pycsl — boolean parameters and operators.
 *
 * `bool_xor` exercises the 0/1-encoded boolean rendering. The
 * translator maps Coq's `xorb` to the integer formula
 * `(a + b) - 2 * (a * b)` and emits `requires (p == 0) or (p == 1)`
 * preconditions for each Bool-typed parameter.
 *)

Require Import Bool.

Definition bool_xor (a b : bool) : bool := xorb a b.

Theorem bool_xor_correct : forall a b : bool, bool_xor a b = xorb a b.
Admitted.
