(*
 * Golden test fixture for rocq2pycsl — ghost_list operations.
 *
 * The theorem mentions `length (l1 ++ l2)` to exercise the
 * Length-distributes-over-Append canonicalizer rewrite that the bridge
 * applies in pycsl_bridge/canonicalizer/normalize.py.
 *)

Require Import List.
Import ListNotations.

Definition list_length_after_append (n : nat) : nat := n.

Theorem list_length_after_append_eq :
  forall (n : nat) (l1 l2 : list nat),
    n + length l1 + length l2 = list_length_after_append n + length (app l1 l2).
Admitted.
