r"""Test 5092 -- gen #37 route #375 (expected PASS): CONTROL: augmented assignments on int locals of a method of a record class, under `no_exception \all`, keep proving.
"""
# pycsl-expected: PASS
from typing import List

class W:
    def __init__(self) -> None:
        self.n = 0

    #@ no_exception \all
    #@ ensures \result == 3
    def m(self, k: int) -> int:
        t = k
        t += 1
        t *= 3
        return t - 3 * k

#@ no_exception \all
#@ ensures \result == 2
def f(xs: List[int]) -> int:
    ys = [1, 2]
    return len(ys)

if __name__ == "__main__":
    assert W().m(5) == 3
    assert f([1]) == 2
