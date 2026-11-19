r"""Test 5800 -- gen #37 route #402 (expected PASS): CONTROL: verified `__hash__` / `__eq__` (`no_exception \all`, no `requires`, `-> int` / `-> bool`) at every kind of hashing site (two- and three-element set displays, a one-element display), an inheriting subclass, a frozen int / str record and a plain identity-eq class (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
from dataclasses import dataclass


class D:
    def __init__(self) -> None:
        self.x: int = 1

    #@ no_exception \all
    def __hash__(self) -> int:
        return self.x

    #@ no_exception \all
    def __eq__(self, o: object) -> bool:
        return False


class E(D):
    pass


@dataclass(frozen=True)
class R:
    a: int
    b: str


class P:
    def __init__(self) -> None:
        self.x: int = 1


#@ no_exception \all
#@ ensures \result == 1
def f(a: D, b: D, e: E, r: R, q: R, p: P, p2: P) -> int:
    t = {a, b, e}
    u = {r, q}
    v = {p, p2}
    return 1


#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    w = {d}
    return 1


if __name__ == "__main__":
    print(f(D(), D(), E(), R(1, "x"), R(1, "x"), P(), P()), g(D()))
