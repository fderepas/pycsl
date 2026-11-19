r"""Test 4692 -- gen #37 route #348: CONTROL: NamedTuple field READ under `no_exception`; PROVES (CPython 1).
"""
from typing import NamedTuple

class N(NamedTuple):
    x: int
    y: int

#@ no_exception \all
def f(n: N) -> int:
    return n.x

if __name__ == "__main__":
    print(f(N(1, 2)))
