r"""Test 1511 - ROUTE #149 (gen #29, found after battery D was frozen): `def __init__(self, k: int = 4): self.x = k * 3` with `C()`; `{ x = 0 }` and `C().x == 0` PROVED at HEAD; CPython 12. The seeded default flows through the captured initialiser.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class C:
    def __init__(self, k: int = 4) -> None:
        self.x = k * 3


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = C()
    return c.x

