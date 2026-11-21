r"""Test 7786 -- route #490 (expected FAIL): route #490 sibling -- `P('a').x + 1` for a dataclass field `x: int` (CPython TypeError) PROVED (or is the same hashed-literal channel) at base 394a1654a; now REFUSED (PYCSL-R490-LITERAL-INT-HASH).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

@dataclass
class P:
    x: int


#@ no_exception \all
def f(n: int) -> int:
    p = P('a')  # type: ignore
    return p.x + 1

if __name__ == "__main__":
    try:
        r = f(0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
