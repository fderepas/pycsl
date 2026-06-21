"""Test 0722 — negative: a caller reaching transfer WITHOUT the capability is caught (H-S).

Same HAPPY as 0721, but `handle` calls `self.transfer(...)` WITHOUT granting the capability.
The injected call-site `#@ check self.session_authenticated == 1` is unprovable in `handle`
(the capability was never established) — the check-before-use violation surfaces as an
unproven VC IN THE CALLER, exactly macsl's `unauth_endpoint` red.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
#@ happy authn:
#@     targets transfer
#@     precond self.session_authenticated == 1
class Bank:
    def __init__(self) -> None:
        self.session_authenticated: int = 0

    #@ requires True
    def transfer(self, amount: int) -> int:
        return amount

    #@ requires True
    def handle(self, amount: int) -> int:
        return self.transfer(amount)           # NO grant -> call-site precond fails in handle
