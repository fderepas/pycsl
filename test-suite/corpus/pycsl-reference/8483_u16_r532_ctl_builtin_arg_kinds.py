r"""Test 8483 -- route #532 (control, expected PASS): builtin and exception-class calls at accepted argument kinds stay field initialisers: `isinstance(n, int)`, `issubclass(bool, int)`, `ValueError("bad")`, `KeyError(n)`, `setattr(self, "x", n)`, and a dataclass `__post_init__(self, m)` matching its InitVar `m`; CPython f(4) returns 1
"""
# pycsl-expected: PASS
from dataclasses import dataclass, InitVar


@dataclass
class D:
    a: int
    m: InitVar[int]

    def __post_init__(self, m: int) -> None:
        self.b = m


class C:
    def __init__(self, n: int) -> None:
        self.i = isinstance(n, int)
        self.s = issubclass(bool, int)
        self.e = ValueError("bad")
        self.k = KeyError(n)
        setattr(self, "x", n)
        self.d = D(n, n)


#@ no_exception \all
#@ ensures \result == 1
def f(n: int) -> int:
    c = C(n)
    return 1


if __name__ == "__main__":
    print(f(4))
