(*
 * Golden test fixture for rocq2pycsl.
 *
 * `double` is a tiny pure function whose two theorems exercise both
 * the basic equality postcondition and the Divides translation rule.
 * Proof bodies are `Admitted.` because the tool treats the .v file as
 * a trusted oracle — what the contracts should say, not whether the
 * proofs hold.
 *)

Require Import ZArith.

Definition double (x : Z) : Z := x * 2.

Theorem double_value : forall x : Z, double x = x * 2.
Admitted.

Theorem double_is_even : forall x : Z, (2 | double x).
Admitted.
