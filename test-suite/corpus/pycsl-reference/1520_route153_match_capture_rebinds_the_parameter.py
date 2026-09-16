r"""Test 1520 - ROUTE #153 carrier-rerun on gen #29's own draft: `match 7: case k: pass` rebinds the parameter `k` through a MatchAs pattern (no Name node); `C(5).x == 5` PROVED at HEAD and on the first draft; CPython 7.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class C:
    def __init__(self, k: int) -> None:
        match 7:
            case k:
                pass
        self.x = k


#@ ensures \result == 5
#@ assigns \nothing
def probe() -> int:
    c = C(5)
    return c.x

