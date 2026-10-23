r"""Test 1832 — gen #31 CONTROL for 1831 (expected FAIL): the same policy on a NON-dunder.

Byte-for-byte 1831 with `__enter__` renamed to `bump`. It FAILED before route #219's repair
and it FAILS after — which is what makes 1831 a ROUTE (the checker exists and worked, and
was switched off by a name) rather than a missing feature.
"""
# pycsl-flags: --memory-model hoare
# pycsl-expected: FAIL
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
