(*
 * Golden test fixture for rocq2pycsl — arrays (Vector.t / array-as-list).
 *
 * The translator treats `array nat` identically to `list nat` (per
 * tuesday-01 plan §1: "PyCSL's `array` ghost type has the same surface
 * ops as `list`"). The Python impl mutates in place — its `#@ assigns`
 * clause has to be added by the user; the translator currently always
 * emits `assigns \nothing`.
 *)

Require Import List.

Definition array_fill_zero (arr : list nat) (n : nat) : nat := n.

Theorem array_fill_zero_correct :
  forall (arr : list nat) (n : nat),
    n <= length arr ->
    array_fill_zero arr n >= 0.
Admitted.
