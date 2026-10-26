r"""Test 5390 -- gen #37 route #381 (expected PASS): CONTROL: hashable outside bases (Exception, int, ABC, NamedTuple, Generic[T], UserString, abc.Sequence) (CPython ok).
"""
# pycsl-expected: PASS
from abc import ABC
from typing import NamedTuple, Generic, TypeVar
from collections import UserString
from collections.abc import Sequence, Iterator

T = TypeVar("T")

class E(Exception):
    pass

class I(int):
    pass

class A(ABC):
    pass

class P(NamedTuple):
    x: int

class G(Generic[T]):
    pass

class S(UserString):
    pass

class Q(Sequence):
    def __getitem__(self, i: int) -> int:
        return 0
    def __len__(self) -> int:
        return 0

#@ no_exception \all
#@ ensures \result == 1
def g(e: E, i: I, a: A, p: P, q: G, s: S, w: Q) -> int:
    t = {e, i, a, p, q, s, w}
    return 1

if __name__ == "__main__":
    print(g(E(), I(3), A(), P(1), G(), S("x"), Q()))
