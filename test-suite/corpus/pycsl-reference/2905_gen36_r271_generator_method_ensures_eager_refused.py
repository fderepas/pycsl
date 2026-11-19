r"""Test 2905 — route #271 (expected FAIL, refused): `bump` contains `yield`, so calling it only
builds a generator and `self.n` is NOT incremented — yet the body was lowered as an ordinary
procedure run at the call, its `ensures self.n == \old(self.n) + 1` proved, and the caller
proved `\result == 1`. CPython `f()` = 0. PROVED at c9d7f157.
"""
# pycsl-expected: FAIL
from typing import Iterator

class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures self.n == \old(self.n) + 1
    #@ assigns self.n
    def bump(self) -> Iterator[int]:
        self.n = self.n + 1
        yield 0

#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    c = C()
    c.bump()
    return c.n

if __name__ == "__main__":
    print(f())
