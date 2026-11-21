r"""Test 7192 -- route #463 (expected FAIL): driver probe (cc1) -- a claimed `class C` (a class invariant) rebound by a second `class C`. Measured on 33f7ac681: FAILED only on a Why3 duplicate-symbol error (`c_v` defined twice), with no message naming the dropped invariant; now REFUSED (route #463) before emission.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ class invariant self.v >= 0
class C:
    def __init__(self) -> None:
        self.v = -1


class C:
    def __init__(self) -> None:
        self.v = -1


#@ ensures \result == n
def f(n: int) -> int:
    return n


if __name__ == "__main__":
    try:
        r = f(1)
        if not (r == 1):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
