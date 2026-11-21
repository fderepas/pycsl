"""Test 1266 — finding w68 CONTROL (NARROWNESS): a foreign-receiver call to a method that is
NOT the guarded target is still allowed.

The rejection in 1265 is keyed on the CALLEE being the H-S target. Calling some other method on
another object assumes no capability and is untouched. This is the rule-(l) negative test for
that repair: a widening of the check to all foreign-receiver calls would turn this file red,
which is the point of keeping it.
"""
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
    #@ assigns \nothing
    def peek(self, other: "Bank", amount: int) -> int:
        return other.balance_of(amount)        # a DIFFERENT method — not a guarded site
