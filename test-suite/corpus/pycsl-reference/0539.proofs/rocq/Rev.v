(* test-suite/corpus/pycsl-reference/0539.proofs/rocq/Rev.v
 *
 * Coq proof of the reversal-permutation framing lemma cited by 0539.py via
 * `#@ proof rocq: Pycsl.Reference.Perm.rev_permutation`. Cross-validated against
 * the Lean statement in 0539.proofs/lean/Rev.lean. No Admitted, no axioms. *)

Require Import List.
Require Import Coq.Sorting.Permutation.

Module Pycsl.
Module Reference.
Module Perm.

(* `permut (array_rev s) s` — reversing a list permutes its elements. The WhyML
   axiom `forall s : array int. permut (array_rev s) s` is the array-model image
   of this list statement (rev l is a permutation of l). *)
(* Coq's `Permutation_rev` is stated `Permutation l (rev l)`; the axiom direction
   is `permut (array_rev s) s` = `Permutation (rev l) l`, so apply symmetry. *)
Theorem rev_permutation : forall (A : Type) (l : list A), Permutation (rev l) l.
Proof. intros A l. apply Permutation_sym. apply Permutation_rev. Qed.

End Perm.
End Reference.
End Pycsl.
