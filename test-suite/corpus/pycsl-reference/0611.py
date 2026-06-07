"""Test 0611 — HAPPY subsystem ownership (`protects`): all writers exempt (07-1143 R1/R2).

A module-level `#@ happy own: protects g.v except setter` declares that no method outside the
owner set `{setter}` may directly write the protected field `g.v`. Here the only writer is the
exempt `setter`; `reader` only reads. So the property expands to zero obligations and the module
proves. Desugars entirely to the per-site `#@ check` primitive — no new IR/backend.
"""
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


#@ ensures \result >= 0
#@ assigns \nothing
def reader() -> int:
    return g.v
