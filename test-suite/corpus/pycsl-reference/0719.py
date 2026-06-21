"""Test 0719 — HAPPY H-E: privilege monotonicity via the general targets/postcond form (positive).

`#@ happy priv_monotonic: targets transfer postcond \forall i; … role[i] >= \old(role[i])`
attaches a NAMED security postcondition to `transfer` (the macsl `\context(\postcond)` form,
see happy-roadmap-impl.md §0a/§0b). Roles are 0=super-admin … 2=user (smaller = MORE
privilege), so "no escalation" is `role[i] >= \old(role[i])`. `transfer` only READS a role
for its RBAC check and never writes one, so the postcondition holds and the file verifies.
"""
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
        r: int = self.role[s]          # RBAC read of the caller's role — no role is written
        if r > 2:
            return -1
        return amount
