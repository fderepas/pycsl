r"""Test 8730 -- route #550 (control, expected PASS): constructors size / truth-test instances whose user dunders are judged (a literal `__len__`, `return self.on`, `return self.n > 0`), and truth-test an instance of a class with no `__bool__` / `__len__`; CPython 1 1
"""
# pycsl-expected: PASS
from dataclasses import dataclass


@dataclass
class Flag:
    on: bool

    def __bool__(self) -> bool:
        return self.on


@dataclass
class Pos:
    n: int

    def __bool__(self) -> bool:
        return self.n > 0


class Two:
    def __len__(self) -> int:
        return 2


class Plain:
    pass


class D:
    def __init__(self, n: int) -> None:
        self.a = 1 if Flag(True) else 0
        self.b = len(Two())
        self.c = 1 if Plain() else 0
        self.d = 1 if Pos(3) else 0


#@ no_exception \all
def g(k: int) -> int:
    d = D(k)
    return 1


if __name__ == "__main__":
    print(g(1), 1)
