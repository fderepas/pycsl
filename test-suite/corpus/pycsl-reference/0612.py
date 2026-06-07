"""Test 0612 — negative: a non-exempt method writing a protected field is caught (07-1143 R1).

Same HAPPY as 0611, but `sneaky` (NOT in the `except` set) directly writes the protected `g.v`.
The meta-pass injects a `#@ check False` at that write site, which is unprovable (the write is
reachable) — surfacing the confinement violation as an unproven VC.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare

#@ happy own:
#@     protects g.v
#@     except setter

#@ class invariant self.v >= 0
class C:
    def __init__(self) -> None:
        self.v: int = 0


g = C()


#@ requires n >= 0
#@ assigns g.v
def setter(n: int) -> None:
    g.v = n


#@ requires n >= 0
#@ assigns g.v
def sneaky(n: int) -> None:
    g.v = n
