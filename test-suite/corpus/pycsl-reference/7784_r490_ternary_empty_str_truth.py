r"""Test 7784 -- route #490 (expected FAIL): route #490 sibling -- `y = 1 if n else ''; return 1 if y else 0` under `ensures \result == 1` (CPython 0 at n == 0: the hash of '' is a non-zero int) PROVED (or is the same hashed-literal channel) at base 394a1654a; now REFUSED (PYCSL-R490-LITERAL-INT-HASH).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ ensures \result == 1
def f(n: int) -> int:
    y = 1 if n else ''
    return 1 if y else 0

if __name__ == "__main__":
    try:
        r = f(0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
