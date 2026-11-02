r"""Test 8215 -- route #516 (control, expected PASS): method results and fields read through a receiver whose class is declared (`p: P`, `self`) take the kinds the class declares (`-> int`, `a: int`), so `p.ga() * p.a` is int arithmetic; CPython f(P(2, 3)) returns 1
"""
# pycsl-expected: PASS
from dataclasses import dataclass


@dataclass
class P:
    a: int
    b: int

    def ga(self) -> int:
        return self.a

    #@ no_exception \all
    #@ ensures \result == 1
    def m(self) -> int:
        w = self.ga() * self.b
        return 1


#@ no_exception \all
#@ ensures \result == 1
def f(p: P) -> int:
    w = p.ga() * p.a
    return 1


if __name__ == "__main__":
    print(f(P(2, 3)))
