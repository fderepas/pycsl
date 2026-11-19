r"""Test 6331 -- route #422 (expected PASS): CONTROL: `str.upper("a")` (an unbound str method: the str row), the `.value` of an Enum member with int initializers, and a nested `def -> int` result, hashed under `no_exception \all` (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
from enum import Enum


class E(Enum):
    A = 1
    B = 2


#@ no_exception \all
def f() -> int:
    def h() -> int:
        return 5
    k = str.upper("a")
    v = E.A.value
    w = h()
    s = {k, v, w}
    return len(s)


if __name__ == "__main__":
    print(f())
