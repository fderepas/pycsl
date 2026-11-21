r"""Test 6984 -- route #455 (expected PASS): CONTROL: `@property` on a method of a class body read through an instance, an `@overload` chain followed by its undecorated implementation, and a module-level `@staticmethod`-free plain def, under `#@ no_exception \all`. Admitted; PROVED at base and candidate (CPython ok).
"""
# pycsl-expected: PASS
from typing import overload


class C:
    def __init__(self) -> None:
        self.v: int = 3

    #@ ensures \result == self.v
    @property
    def size(self) -> int:
        return self.v


@overload
def g(a: int) -> int:
    ...


#@ ensures \result == a
def g(a: int) -> int:
    return a


#@ no_exception \all
#@ ensures \result == n
def f(n: int) -> int:
    return g(n)


if __name__ == "__main__":
    print(f(2), C().size)
