"""Test 0720 — negative: a transfer that LOWERS a role (escalation) fails priv_monotonic (H-E).

Same HAPPY as 0719, but `transfer` writes `self.role[s] = 0` (0 = more privilege) — a
confused-deputy escalation. The attached `priv_monotonic` postcondition
`role[s] >= \old(role[s])` is then violated and the postcondition VC is unprovable.
(The macsl twin is attacks.c's confused-deputy red.)
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
#@ class invariant \length(self.role) >= 5
#@ happy priv_monotonic:
#@     targets transfer
#@     postcond \forall i; (0 <= i and i < 5) ==> self.role[i] >= \old(self.role[i])
class Bank:
    def __init__(self) -> None:
        self.role: list = bytearray(5)

    #@ requires 0 <= s and s < 5
    def transfer(self, s: int, amount: int) -> int:
        self.role[s] = 0               # ESCALATION: lowers a role -> violates monotonicity
        return amount
