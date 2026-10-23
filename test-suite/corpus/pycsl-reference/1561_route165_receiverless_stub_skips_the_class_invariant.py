r"""Test 1561 - ROUTE #165 (gen #29): `class invariant self.x >= 0`; `c = C(); c.x = -5; return c.get()` with `get` ensuring `\result >= 0` - the method call became the receiver-less stub `val c_get_0 () : int ensures { result >= 0 }`, so the broken invariant was never checked and `\result >= 0` PROVED; CPython -5. The receiver is now passed, so Why3 demands the invariant at the call.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ class invariant self.x >= 0
class C:
    def __init__(self) -> None:
        self.x = 1

    #@ ensures \result >= 0
    def get(self) -> int:
        return self.x


#@ ensures \result >= 0
def probe() -> int:
    c = C()
    c.x = -5
    return c.get()

