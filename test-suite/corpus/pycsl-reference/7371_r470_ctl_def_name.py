r"""Test 7371 -- route #470 (expected PASS): CONTROL -- an annotated def and class whose
`__name__` / `__qualname__` (faithfully synthesized) are read at module level, never their
`__annotations__`. PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import List


def g(x: int) -> int:
    return x


class C:
    y: int = 0

    def m(self, z: int) -> int:
        return z


X = g.__name__
Y = C.m.__qualname__
Z = C.y


#@ requires n >= 0
#@ ensures \result == n + 1
#@ no_exception \all
def f(n: int) -> int:
    return n + 1


if __name__ == "__main__":
    print(f(1), X, Y, Z)
