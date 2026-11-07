r"""Test 1512 - ROUTE #149 (gen #29) positive twin of 1511: `C().x == 12` PROVES (FAILS at HEAD).
"""
_ = 0  # anchor


class C:
    def __init__(self, k: int = 4) -> None:
        self.x = k * 3


#@ ensures \result == 12
#@ assigns \nothing
def probe() -> int:
    c = C()
    return c.x

