r"""Test 7186 -- route #463 (expected FAIL): driver probe (cc1) -- `#@ assert y == 2` written after code on its line is a plain comment. Measured on 33f7ac681: PROVED; now REFUSED (route #463).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ ensures \result == n
def f(n: int) -> int:
    y = n + 1  #@ assert y == 2
    return n


if __name__ == "__main__":
    try:
        r = f(5)
        if not (r == 5):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
