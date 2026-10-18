r"""Test 2906 — route #271 (expected FAIL, refused): no claim on the generator itself, but
`g.bump()` on a MODULE-GLOBAL instance is INLINED (inline.md), so the generator's body —
`self.n = self.n + 1` — was spliced into the caller and `ensures g.n == 1` proved. CPython:
calling `g.bump()` only builds a generator, `g.n` stays 0. PROVED at c9d7f157.
"""
# pycsl-expected: FAIL
from typing import Iterator

class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ assigns self.n
    def bump(self) -> Iterator[int]:
        self.n = self.n + 1
        yield 0

g = C()

#@ ensures g.n == 1
#@ assigns g.n
def f() -> None:
    g.n = 0
    g.bump()

if __name__ == "__main__":
    f()
    print(g.n)
