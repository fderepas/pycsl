r"""Test 1717 — ROUTE #209 CONTROL: the same trusted writer, opting in with `#@ \preserves`.

R1.1's rule is not "a trusted function may not write a protected path" — it is "it must say
so". With `#@ \preserves` present the promise is explicit and the program is accepted,
exactly as 0461 is accepted for the REGION form. If this file ever fails, route #209's
repair has turned a trust boundary into a ban.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
_ = 0  # anchor

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
#@ \preserves
#@ \trusted
def declared_stub(n: int) -> None:
    g.v = n
