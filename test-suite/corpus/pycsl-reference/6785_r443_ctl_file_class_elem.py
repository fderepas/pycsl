r"""Test 6785 -- route #443 (expected PASS): CONTROL -- an element of `List[C]` for a file class `C` as a method receiver; PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import List


class C:
    def __init__(self, n: int) -> None:
        self.n = n

    #@ no_exception \all
    def size(self) -> int:
        return 1


#@ no_exception \all
def f(xs: List[C]) -> int:
    if len(xs) == 0:
        return 0
    return xs[0].size()


if __name__ == "__main__":
    print("result", f([C(1)]))
