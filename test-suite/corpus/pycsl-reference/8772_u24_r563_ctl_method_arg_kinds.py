r"""Test 8772 -- route #563 (control, expected PASS): method calls whose arguments are of the declared parameter kinds: an int parameter, `len(t)` of a str, an int keyword argument, a str into a str parameter, a construction then a call; CPython 2 3 2 2 2
"""
# pycsl-expected: PASS
from dataclasses import dataclass


@dataclass
class P:
    a: int

    def m(self, y: int) -> int:
        return self.a + y

    def n(self, s: str) -> int:
        return len(s)


#@ no_exception \all
def f1(k: int, t: str, p: P) -> int:
    return p.m(k)


#@ no_exception \all
def f2(k: int, t: str, p: P) -> int:
    return p.m(len(t))


#@ no_exception \all
def f3(k: int, t: str, p: P) -> int:
    return p.m(y=k)


#@ no_exception \all
def f4(k: int, t: str, p: P) -> int:
    return p.n(t)


#@ no_exception \all
def f5(k: int, t: str, p: P) -> int:
    return P(1).m(k)


if __name__ == "__main__":
    print(f1(1, "ab", P(1)), f2(1, "ab", P(1)), f3(1, "ab", P(1)), f4(1, "ab", P(1)), f5(1, "ab", P(1)))
