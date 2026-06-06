"""Test 0579 — negative: inlined method, wrong post-state is unprovable (Phase 2).

Same as 0578 but the postcondition over-claims `+ amount + 1`. After inlining the real
field write `acc.balance <- acc.balance + amount`, the VC refutes it. Confirms the inlined
frame is exact, not vacuous.
"""
# pycsl-expected: FAIL
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
#@ ensures acc.balance == \old(acc.balance) + amount + 1
#@ assigns acc.balance
def do_deposit(amount: int) -> None:
    acc.deposit(amount)
