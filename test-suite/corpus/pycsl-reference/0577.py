"""Test 0577 — negative: a false fact about a module global is unprovable (Phase 1).

Same global as 0576, but the postcondition claims `\result == acc.balance + 1` while the
body returns `acc.balance` — false, so verification fails. Confirms the global-state model
is not vacuously true.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare

#@ class invariant self.balance >= 0
class Account:
    def __init__(self) -> None:
        self.balance: int = 0


acc = Account()


#@ ensures \result == acc.balance + 1
#@ assigns \nothing
def peek() -> int:
    return acc.balance
