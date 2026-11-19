r"""Test 7372 -- route #471 (expected PASS): CONTROL -- class statements inside function bodies
that CPython creates without raising: a plain local class and a subclass of it, a local `@dataclass` with an
immutable default, a local Enum, a local NamedTuple, a local `Exception` subclass, a
class in a method and in an `if` arm, a local class with `__slots__` and no conflicting class
variable.
PROVED at base and candidate.
"""
# pycsl-expected: PASS
from dataclasses import dataclass
from enum import Enum
from typing import List, NamedTuple


class Base:
    pass


def helper(n: int) -> int:
    class Plain:
        pass

    class Sub(Plain):
        pass

    @dataclass
    class Rec:
        total: int = 0

    class Color(Enum):
        RED = 1
        GREEN = 2

    class Pt(NamedTuple):
        x: int
        y: int = 0

    class Oops(Exception):
        pass

    class Sl(Base):
        __slots__ = ("a",)

    if n > 0:
        class Arm:
            pass
    return n


class Host:
    def meth(self) -> int:
        class Inner:
            z = 1
        return 1


#@ requires n >= 0
#@ ensures \result == n + 1
#@ no_exception \all
def f(n: int) -> int:
    return n + 1


if __name__ == "__main__":
    print(f(1), helper(1), Host().meth())
