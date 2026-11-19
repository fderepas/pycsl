r"""Test 7785 -- route #490 (expected FAIL): route #490 sibling -- `g()` for `def g(x: int = None) -> int: return x + 1` (CPython TypeError) PROVED (or is the same hashed-literal channel) at base 394a1654a; now REFUSED (PYCSL-R490-LITERAL-INT-HASH).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

def g(x: int = None) -> int:  # type: ignore
    return x + 1


#@ no_exception \all
def f(n: int) -> int:
    return g()

if __name__ == "__main__":
    try:
        r = f(0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
