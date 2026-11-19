r"""Test 2901 — route #270 (expected FAIL, refused): `fail()` ends in `raise` and has no `return`,
so #264's no-return rule ended the `else` path at the call — but `fail` is a GENERATOR: calling
it only builds the generator, so control falls through to `return y` with `y` unbound. CPython
`f(False)` raises `UnboundLocalError` (not `ValueError`). PROVED at c9d7f157.
"""
# pycsl-expected: FAIL
from typing import Iterator

#@ raises ValueError when True
#@ assigns \nothing
def fail() -> Iterator[int]:
    yield 1
    raise ValueError("x")

#@ ensures \result >= 0
#@ raises ValueError when not c
#@ assigns \nothing
def f(c: bool) -> int:
    if c:
        y = 1
    else:
        fail()
    return y

if __name__ == "__main__":
    try:
        print(f(False))
    except Exception as exc:
        print(type(exc).__name__, exc)
