r"""Test 3755 -- gen #37 ch34 (expected PASS): a MODULE-LEVEL function whose parameter is NAMED `self`. Module 5 dropped every parameter named `self`, methods or not, so the free function lost it from its scope and signature and every read became an unbound `self` symbol (fail-closed, but unverifiable); only a METHOD's receiver is dropped now, a free function's `self` is an ordinary parameter. Honest claims must PROVE.
"""


class Box:
    def __init__(self, v: int) -> None:
        self.v = v


def succ(self: int) -> int:
    return self + 1


def get(self: Box) -> int:
    return self.v


#@ ensures \result == 4
#@ assigns \nothing
def use_succ() -> int:
    return succ(3)


#@ ensures \result == 5
#@ assigns \nothing
def use_get() -> int:
    b = Box(5)
    return get(b)
