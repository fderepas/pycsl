"""Test 0341 — PyCSL class invariant + cross-prover methods (tuesday-01 Phase 6).

The Coq/Lean `bank_account` fixtures generate per-method contracts
for `deposit` and `withdraw`. The bridge applies an `arg_map` rewrite
so the proof-side `balance` parameter becomes `self._balance` on the
Python side. The class invariant is preserved from the source.

Verified end-to-end under full proof mode (no `--no-proof`, no
`\\trusted`). Module6 emits the class as a Why3 record with the
invariant `self._balance >= 0` attached at the type level, and the
mutation postconditions `self._balance == \\old(self._balance) ± amount`
discharge as linear-arithmetic VCs against the field-update model.
"""
#@ class invariant self._balance >= 0
class BankAccount:
    def __init__(self) -> None:
        self._balance: int = 0

    #@ requires self._balance >= 0
    #@ requires amount >= 0
    #@ ensures self._balance == \old(self._balance) + amount
    #@ assigns self._balance
    def deposit(self, amount: int) -> None:
        self._balance = self._balance + amount

    #@ requires self._balance >= 0
    #@ requires amount >= 0
    #@ requires amount <= self._balance
    #@ ensures self._balance == \old(self._balance) - amount
    #@ assigns self._balance
    def withdraw(self, amount: int) -> None:
        self._balance = self._balance - amount
