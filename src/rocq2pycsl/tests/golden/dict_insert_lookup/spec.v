(*
 * Golden test fixture for rocq2pycsl — dicts represented as
 * `nat -> option nat` (a characteristic-function-style finite map).
 *
 * The theorem asserts that inserting `v` at key `k` and immediately
 * returning the inserted value is `v` — independent of `d` and `k`.
 * Exercises the arrow type in the binder (`nat -> option nat`).
 *)

Definition dict_insert_lookup (d : nat -> option nat) (k v : nat) : nat := v.

Theorem dict_insert_lookup_correct :
  forall (d : nat -> option nat) (k v : nat),
    dict_insert_lookup d k v = v.
Admitted.
