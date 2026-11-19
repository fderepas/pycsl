r"""Test 2661 — route #257 (expected FAIL): a bare `with b.bump():` over an IN-FILE
`@contextmanager` METHOD that writes `self.n` before it yields. The file defines no
`__enter__`, so the route #38/#39 guard never ran and the `with` header was erased;
`\result == 0` PROVED at 49f6a35d. CPython: the generator body runs on entry, f() == 1.
Now REFUSED fail-closed.
"""
# pycsl-expected: FAIL
from contextlib import contextmanager
from typing import Iterator


class Box:
    #@ ensures self.n == 0
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures self.n == \old(self.n) + 1
    #@ assigns self.n
    @contextmanager
    def bump(self) -> Iterator[int]:
        self.n = self.n + 1
        yield 0


#@ ensures \result == 0
def f() -> int:
    b = Box()
    with b.bump():
        pass
    return b.n


if __name__ == "__main__":
    assert f() == 1
