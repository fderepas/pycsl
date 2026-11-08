r"""Test 8638 -- route #553 (expected FAIL: PROVED at base int28, now NOT PROVED on a `PyCSL-R521` obligation; u21 caller-side twin of red team 52 bm1200): the callee HONESTLY annotates `xs: List[Optional[int]]` and stores None; the caller passes its own `[1]` and reads `xs[0] + 1` -- the caller's list is tainted by the call; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ requires len(xs) >= 1
def g(xs: List[Optional[int]]) -> None:
    xs[0] = None


#@ no_exception \all
def f(k: int) -> int:
    xs = [1]
    g(xs)
    return xs[0] + 1


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
