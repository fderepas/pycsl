"""Test 0578 — inline a mutating method on a global; prove a field-referencing post (Phase 2).

`do_deposit` calls `acc.deposit(amount)` on the module global `acc`. The call is INLINED:
`deposit`'s body `self.balance += amount` is spliced with self→acc, giving
`acc.balance <- acc.balance + amount`. The caller's VC then sees the exact field write, so
the field-referencing postcondition `acc.balance == \old(acc.balance) + amount` discharges —
which the modular contract path CANNOT prove (the method-call contract gap A2c: a method's
self-field ensures does not propagate to a constructing/calling driver). Inlining closes it.
"""
# pycsl-flags: --memory-model hoare

#@ class invariant self.balance >= 0
class Account:
    def __init__(self) -> None:
        self.balance: int = 0

    #@ requires amount >= 0
    #@ ensures self.balance == \old(self.balance) + amount
    #@ assigns self.balance
    def deposit(self, amount: int) -> None:
        self.balance += amount


acc = Account()


#@ requires amount >= 0
#@ ensures acc.balance == \old(acc.balance) + amount
#@ assigns acc.balance
def do_deposit(amount: int) -> None:
    acc.deposit(amount)
