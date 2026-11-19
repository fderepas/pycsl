"""Test 1265 — finding w68, NEGATIVE: an H-S guarded call through a non-`self` receiver.

`#@ happy authn: targets transfer precond …` has two halves — the TARGET assumes the capability
as a `requires` (MEASURED: real), and every CALL SITE must prove it via a `#@ check` injected by
`_collect_self_call_sites`, which matches ONLY `self.<target>(…)`. A call through any other
receiver is not a site, gets no check, and the target still assumes the capability.

BEFORE THIS REJECTION the asymmetry was fenced only by a COMPLETENESS GAP: a non-`self` call is
OPAQUE in the model and propagates no postcondition at all (w68 measured this as its aliveness
control, and it is what made w68's own exploit probe VACUOUS). The day cross-object calls carry
their callee's contract — an obvious gain, since today it makes every cross-object call useless
for proof — the capability becomes assumable at a call site nobody checks.

INJECTING the check here instead would be UNSOUND, and that is why the resolution is rejection:
the guarding formula speaks about `self`, so discharging it at `other.transfer(…)` would prove
the capability of the WRONG OBJECT. The check is keyed on the CALLEE, not on the receiver's
shape — route #91's lesson, key on what is being called.
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
    #@ assigns \nothing
    def attack(self, other: "Bank", amount: int) -> int:
        return other.transfer(amount)          # no grant, and no check was ever injected
