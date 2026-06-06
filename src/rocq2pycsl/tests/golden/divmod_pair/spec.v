(*
 * Golden test fixture for rocq2pycsl — tuple return values.
 *
 * `divmod_pair a b` returns `(a/b, a mod b)`. The two theorems exercise
 * Coq's `fst` and `snd` projections → IR `Proj` nodes, which render as
 * `\result[0]` / `\result[1]` in the PyCSL contract.
 *)

Require Import ZArith.

Definition divmod_pair (a b : Z) : Z * Z := (a div b, a mod b).

Theorem divmod_pair_fst : forall (a b : Z),
  b <> 0 -> fst (divmod_pair a b) = a div b.
Admitted.

Theorem divmod_pair_snd : forall (a b : Z),
  b <> 0 -> snd (divmod_pair a b) = a mod b.
Admitted.
