r"""Test 5043 -- gen #37 route #371 (expected PASS): CONTROL: `D(N, M)`, `N.__hash__` comes first in the MRO, `M.__hash__ = None` is shadowed: hashable (CPython ok). Route #402: the `__hash__` a hashing site calls carries a verified `#@ no_exception \all` contract.
"""
# pycsl-expected: PASS
class M:
    __hash__ = None


class N:
    #@ no_exception \all
    def __hash__(self) -> int:
        return 1


class D(N, M):
    def __init__(self) -> None:
        self.x = 1


#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    s = {d}
    return 1


if __name__ == "__main__":
    print(g(D()))
