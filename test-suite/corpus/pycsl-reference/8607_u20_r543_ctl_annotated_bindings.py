r"""Test 8607 -- route #543 (control, expected PASS): `x: P = P(k)`, `m: C = C.A`, `xs: List[P] = [P(1)]`, `x: Optional[P] = None` tested before use; CPython 3 1 1 0
"""
# pycsl-expected: PASS
import enum
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class P:
    a: int


class C(enum.Enum):
    A = 1


#@ no_exception \all
def f(k: int) -> int:
    x: P = P(k)
    return x.a


#@ no_exception \all
def g(k: int) -> int:
    m: C = C.A
    return m.value


#@ no_exception \all
def h(k: int) -> int:
    xs: List[P] = [P(1)]
    return xs[0].a


#@ no_exception \all
def u(k: int) -> int:
    x: Optional[P] = None
    if x is None:
        return 0
    return x.a


if __name__ == "__main__":
    print(f(3), g(0), h(0), u(0))
