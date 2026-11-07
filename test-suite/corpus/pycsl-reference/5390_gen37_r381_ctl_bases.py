r"""Test 5390 -- gen #37 route #381 (expected PASS): CONTROL: hashable outside bases the model has (Exception, ABC, NamedTuple, Generic[T]) (CPython ok). The int / UserString / abc.Sequence bases of the original r381s control are refused by systematic rule S1 (unmodelled base) and live in 5394.
"""
# pycsl-expected: PASS
from abc import ABC
from typing import NamedTuple, Generic, TypeVar

T = TypeVar("T")

class E(Exception):
    pass

class A(ABC):
    pass

class P(NamedTuple):
    x: int

class G(Generic[T]):
    pass

#@ no_exception \all
#@ ensures \result == 1
def g(e: E, a: A, p: P, q: G) -> int:
    t = {e, a, p, q}
    return 1

if __name__ == "__main__":
    print(g(E(), A(), P(1), G()))
