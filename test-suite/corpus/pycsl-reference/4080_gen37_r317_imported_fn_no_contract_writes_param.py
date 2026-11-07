r"""Test 4080 -- gen #37 route #317 (expected FAIL): imported `poke(xs)` with no contract does `xs[0] = 5`; its `val` had no writes and `ys[0] == 0` PROVED (CPython 5). The `val` now writes `xs`: FAILS.
"""
# pycsl-expected: FAIL
from typing import List
from multi_file_lib.rt16helper import poke

#@ ensures \result == 0
def f() -> int:
    ys = [0]
    poke(ys)
    return ys[0]

if __name__ == "__main__":
    assert f() == 0, f()
