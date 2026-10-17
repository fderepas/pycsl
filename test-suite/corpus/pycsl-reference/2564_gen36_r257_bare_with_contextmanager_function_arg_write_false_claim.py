r"""Test 2564 — route #257 (expected FAIL): a bare `with bump(b):` over an IN-FILE
module-level `@contextmanager` function that writes its ARGUMENT's field (the class itself
defines no `__enter__`, so the route #38/#39 guard never ran). CPython: f() == 1.
Now REFUSED fail-closed.
"""
# pycsl-expected: FAIL
from contextlib import contextmanager
from typing import Iterator


class Box:
    #@ ensures self.n == 0
    def __init__(self) -> None:
        self.n: int = 0


#@ ensures b.n == \old(b.n) + 1
#@ assigns b.n
@contextmanager
def bump(b: Box) -> Iterator[int]:
    b.n = b.n + 1
    yield 0


#@ ensures \result == 0
def f() -> int:
    b = Box()
    with bump(b):
        pass
    return b.n


if __name__ == "__main__":
    assert f() == 1
