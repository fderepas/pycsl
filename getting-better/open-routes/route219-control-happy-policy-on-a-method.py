# pycsl-flags: --memory-model hoare
# ROUTE #219 CONTROL 3 (expects FAILED today — the policy being enforced).
#
# Byte-for-byte route219-carrier-happy-policy-on-a-dunder.py with `__enter__` renamed to
# `bump`.
#@ happy no_decrease:
#@     targets bump
#@     postcond self.v >= \old(self.v)
class C:
    def __init__(self) -> None:
        self.v: int = 5

    #@ assigns self.v
    def bump(self) -> int:
        self.v = 0
        return 0
