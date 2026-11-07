r"""Test 5149 -- gen #37 route #379 (expected FAIL): an inline display `D(**{"x": 5}).x == 0` (CPython 5). PROVED at base b815ee8d8.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

@dataclass
class D:
    x: int

#@ ensures \result == 0
def f() -> int:
    d = D(**{"x": 5})
    return d.x

if __name__ == "__main__":
    print(f())
