r"""Test 1489 - ROUTE #149 (gen #29) positive twin of 1482: `Cy(r=9)` with `q` defaulted to 1 gives 5, and PROVES (FAILS at HEAD).
"""
_ = 0  # anchor


class Cy:
    def __init__(self, q: int = 1, r: int = 5) -> None:
        self.q = q
        self.r = r


#@ ensures \result == 5
#@ assigns \nothing
def probe() -> int:
    c = Cy(r=9)
    return c.r - c.q + 1 - 4
