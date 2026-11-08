r"""Test 5041 -- gen #37 route #369 (expected PASS): CONTROL: well-formed calls of an explicit `__init__` with defaults / kw-only and of a dataclass with a required `field(kw_only=True)` (CPython ok).
"""
# pycsl-expected: PASS
from dataclasses import dataclass, field


class P:
    def __init__(self, a: int, b: int = 2, *, c: int = 3) -> None:
        self.a = a
        self.b = b
        self.c = c


@dataclass
class Q:
    x: int = field(kw_only=True)
    y: int = 0


#@ no_exception \all
#@ ensures \result == 9
def f() -> int:
    p = P(1, c=5)
    q = Q(3, x=1)
    r = P(a=1, b=2)
    return p.a + p.c + q.y
#   1 + 5 + 3 = 9


if __name__ == "__main__":
    print(f())
