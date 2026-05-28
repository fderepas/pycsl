(* test-suite/corpus/pycsl-reference/0342.proofs/rocq/gcd.v
 *
 * Coq proofs of the Euclidean GCD postconditions stated in 0342.py.
 * Referenced by `#@ proof rocq: Pycsl.Reference.Gcd.<thm>` directives.
 *
 * Verified under Coq 8.20.1. The proofs use Coq.Init.Nat.gcd and
 * stdlib lemmas — no Admitted, no axioms. *)

Require Import Coq.Init.Nat.
Require Import Coq.Arith.PeanoNat.
Require Import Lia.

Module Pycsl.
Module Reference.
Module Gcd.

(* `\result >= 0` — `Nat.gcd` returns a `nat`, non-negative by construction. *)
Theorem gcd_result_nonneg : forall a b : nat, Nat.gcd a b >= 0.
Proof. intros. lia. Qed.

(* `(a > 0 \/ b > 0) ==> \result > 0`. *)
Theorem gcd_result_positive : forall a b : nat,
  a > 0 \/ b > 0 -> Nat.gcd a b > 0.
Proof.
  intros a b H.
  destruct (Nat.gcd a b) eqn:Hg.
  - apply Nat.gcd_eq_0 in Hg. lia.
  - lia.
Qed.

(* `(a > 0 \/ b > 0) ==> a mod \result = 0`. *)
Theorem gcd_divides_a : forall a b : nat,
  a > 0 \/ b > 0 -> a mod (Nat.gcd a b) = 0.
Proof.
  intros a b H.
  apply Nat.Lcm0.mod_divide.
  apply Nat.gcd_divide_l.
Qed.

(* `(a > 0 \/ b > 0) ==> b mod \result = 0`. *)
Theorem gcd_divides_b : forall a b : nat,
  a > 0 \/ b > 0 -> b mod (Nat.gcd a b) = 0.
Proof.
  intros a b H.
  apply Nat.Lcm0.mod_divide.
  apply Nat.gcd_divide_r.
Qed.

(* Loop-exit collapse: `gcd a 0 = a`. Matches the WhyML axiom `gcd_0`,
   which lets the loop invariant `gcd(x, y) == gcd(a, b)` discharge
   the postcondition once `y` reaches 0. *)
Theorem gcd_0 : forall a : nat, Nat.gcd a 0 = a.
Proof. intros a. apply Nat.gcd_0_r. Qed.

(* Euclidean step: `gcd a b = gcd b (a mod b)` when `b > 0`. Matches the
   WhyML axiom `gcd_step`, the load-bearing invariant-preservation lemma
   for the Euclidean loop body. *)
Theorem gcd_step : forall a b : nat,
  b > 0 -> Nat.gcd a b = Nat.gcd b (a mod b).
Proof.
  intros a b Hb.
  rewrite (Nat.gcd_comm a b).
  destruct b as [|b']; [lia|].
  change (Nat.gcd (a mod S b') (S b') = Nat.gcd (S b') (a mod S b')).
  apply Nat.gcd_comm.
Qed.

(* Maximality: any positive common divisor `k` of `a` and `b` is at most
   `Nat.gcd a b`. This is the load-bearing axiom that turns the contract
   from "result is *a* common divisor" into "result is the *greatest*
   common divisor". Matches the WhyML axiom `gcd_greatest`. *)
Theorem gcd_greatest : forall a b k : nat,
  a > 0 \/ b > 0 -> k > 0 -> a mod k = 0 -> b mod k = 0 ->
  k <= Nat.gcd a b.
Proof.
  intros a b k Hab Hk Ha Hb.
  apply Nat.divide_pos_le.
  - apply gcd_result_positive; exact Hab.
  - apply Nat.gcd_greatest;
    [ apply Nat.Lcm0.mod_divide; exact Ha
    | apply Nat.Lcm0.mod_divide; exact Hb ].
Qed.

End Gcd.
End Reference.
End Pycsl.
