r"""Test 5394 -- gen #37 systematic rule S1 (expected FAIL, REFUSED): the int / UserString / collections.abc.Sequence bases split out of control 5390 at integration. CPython hashes all three fine, but PyCSL has no model of these bases, so S1 refuses them (PYCSL-S1-UNMODELLED-BASE). That is a sound over-refusal, recorded so it stays visible.
"""
# pycsl-expected: FAIL
from collections import UserString
from collections.abc import Sequence

class I(int):
    pass

class S(UserString):
    pass

class Q(Sequence):
    def __getitem__(self, i: int) -> int:
        return 0
    def __len__(self) -> int:
        return 0

#@ no_exception \all
#@ ensures \result == 1
def g(i: I, s: S, w: Q) -> int:
    t = {i, s, w}
    return 1

if __name__ == "__main__":
    print(g(I(3), S("x"), Q()))
