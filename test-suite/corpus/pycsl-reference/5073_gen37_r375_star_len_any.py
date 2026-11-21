r"""Test 5073 -- gen #37 route #375 (expected FAIL): NEW shape (no `no_exception`): `xs = [*x]` for `x: Any` was the one-element array, so `len(xs) == 1` PROVED (CPython len(x), 2 for [1, 2]). FAILS now (the starred erased element is not modelled).
"""
# pycsl-expected: FAIL
from typing import Any

#@ ensures \result == 1
def f(x: Any) -> int:
    xs = [*x]
    return len(xs)

if __name__ == "__main__":
    assert f([1, 2]) == 1, f([1, 2])
