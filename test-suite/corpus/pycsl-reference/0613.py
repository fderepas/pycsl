"""Test 0613 — negative: aliasing a protected base is rejected (07-1143 R2 soundness).

A non-exempt method binds the protected base `g` to a local (`x = g`) and writes through it
(`x.v = 99`) — which would evade the per-site write check. PyCSL rejects aliasing of a protected
base at parse/weave time (sound-by-rejection, not deferred), so confinement cannot be bypassed.
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


#@ assigns g.v
def setter(n: int) -> None:
    g.v = n


#@ assigns \nothing
def evade() -> None:
    x = g
    x.v = 99
