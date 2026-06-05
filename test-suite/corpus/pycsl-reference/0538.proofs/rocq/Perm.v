(* test-suite/corpus/pycsl-reference/0538.proofs/rocq/Perm.v
 *
 * Coq proof of the permutation reflexivity axiom cited by 0538.py via
 * `#@ proof rocq: Pycsl.Reference.Perm.permut_refl`. Cross-validated against
 * the Lean statement in 0538.proofs/lean/Perm.lean. No Admitted, no axioms. *)

Require Import List.
Require Import Coq.Sorting.Permutation.

Module Pycsl.
Module Reference.
Module Perm.

(* `permut s s` — `\permutation(a, a)`: a list is a permutation of itself.
   The WhyML axiom `forall s : array int. permut s s` is the array-model image
   of this list statement. *)
Theorem permut_refl : forall (A : Type) (l : list A), Permutation l l.
Proof. intros A l. apply Permutation_refl. Qed.

End Perm.
End Reference.
End Pycsl.
