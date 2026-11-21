r"""Test 2361 — route #247 (expected PASS): CONTROL. A record/variant tag still decides the SAME declared
class: `r: pa` decides `isinstance(r, pa)` TRUE (CPython `f(pa(1))` = 1; a subclass is an instance too).
"""
# pycsl-expected: PASS


class pa:
    def __init__(self, v: int) -> None:
        self.v = v


#@ ensures \result == 1
#@ assigns \nothing
def f(r: pa) -> int:
    if isinstance(r, pa):
        return 1
    return 0


if __name__ == "__main__":
    assert f(pa(1)) == 1
