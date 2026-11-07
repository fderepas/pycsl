r"""Test 4996 -- gen #37 route #369 (expected FAIL): `t.ClassVar` recognised, but `D(1, 5)` past it was never arity-checked (CPython raises / violates; PROVED at base dc378283).
"""
# pycsl-expected: FAIL
import typing as t
from dataclasses import dataclass

@dataclass
class D:
    x: int
    k: t.ClassVar[int] = 3

#@ no_exception \all
def f() -> int:
    d = D(1, 5)
    return d.x

if __name__ == "__main__":
    print(f())
