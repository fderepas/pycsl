r"""Test 7370 -- route #469 (expected PASS): CONTROL -- the module dunders bound but not used in a
computation that could raise: `X = __name__` (unused), `P = __package__`, a class whose
`__name__` / `__qualname__` are read, and the canonical `if __name__ == "__main__":` driver
(not judged at import). PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import List

X = __name__
P = __package__


class C:
    pass


N = C.__name__
Q = C.__qualname__
L = len(C.__qualname__)


#@ requires n >= 0
#@ ensures \result == n + 1
#@ no_exception \all
def f(n: int) -> int:
    return n + 1


if __name__ == "__main__":
    print(f(1), X, P, N, Q, L)
