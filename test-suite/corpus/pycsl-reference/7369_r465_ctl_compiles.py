# -*- coding: utf-8 -*-
r"""Test 7369 -- route #465 (expected PASS): CONTROL -- a module CPython compiles: a `utf-8`
coding cookie over non-ASCII text (café), `from __future__ import annotations` after the
docstring, a `global` read of a module name (not a parameter), an `async def` with `await`, a
generator with `yield`, and the `__main__` driver. PROVED at base
and candidate (compile() succeeds, the decoded text is the verified text).
"""
# pycsl-expected: PASS
from __future__ import annotations

COUNT = 0


def read_count() -> int:
    global COUNT
    return COUNT


async def later(x: int) -> int:
    return x


async def caller(x: int) -> int:
    return await later(x)


def gen(n: int):
    yield n


#@ requires n >= 0
#@ ensures \result == n + 1
#@ no_exception \all
def f(n: int) -> int:
    return n + 1


if __name__ == "__main__":
    print(f(1))
