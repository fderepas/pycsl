(*
 * Golden test fixture for rocq2pycsl — ghost_set, represented as
 * `nat -> bool` (characteristic-function form).
 *
 * The theorem quantifies over two such sets to exercise the arrow-type
 * grammar production and the `Nat -> Bool`/`nat -> bool` type
 * normalization in the bridge's canonicalizer.
 *)

Definition set_union_eq (n : nat) : nat := n.

Theorem set_union_eq_correct :
  forall (n : nat) (s1 s2 : nat -> bool),
    set_union_eq n = n.
Admitted.
