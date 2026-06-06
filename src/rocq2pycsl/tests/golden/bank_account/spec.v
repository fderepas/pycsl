(*
 * Golden test fixture for rocq2pycsl — class methods.
 *
 * BankAccount is modeled in Coq as a record-as-function-on-balance.
 * Each method theorem treats the receiver as a `balance` parameter,
 * matching the surface form `self._balance` in PyCSL contracts. The
 * Python class is hand-annotated with a `#@ class invariant` line so
 * the bridge's per-method contracts compose into a verifiable class.
 *)

Definition deposit (balance amount : nat) : nat := balance + amount.

Definition withdraw (balance amount : nat) : nat := balance - amount.

Theorem deposit_post : forall (balance amount : nat),
  deposit balance amount = balance + amount.
Admitted.

Theorem withdraw_post : forall (balance amount : nat),
  amount <= balance ->
  withdraw balance amount = balance - amount.
Admitted.
