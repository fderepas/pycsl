-- Golden test fixture for lean2pycsl — class methods.
--
-- Mirrors src/rocq2pycsl/tests/golden/bank_account. The Lean side
-- models the receiver as a `balance` parameter — the same shape as
-- the Coq side — so the cross-prover IR matches.

def deposit (balance amount : Nat) : Nat := balance + amount

def withdraw (balance amount : Nat) : Nat := balance - amount

@[pycsl_spec "BankAccount.deposit"]
theorem deposit_post : ∀ (balance amount : Nat),
  deposit balance amount = balance + amount := sorry

@[pycsl_spec "BankAccount.withdraw"]
theorem withdraw_post : ∀ (balance amount : Nat),
  amount <= balance →
  withdraw balance amount = balance - amount := sorry
