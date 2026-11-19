r"""Test 7783 -- route #490 (expected FAIL): route #490 sibling -- `a = [1]; a.append('x'); a[1] + 1` (CPython TypeError) PROVED (or is the same hashed-literal channel) at base 394a1654a; now REFUSED (PYCSL-R490-LITERAL-INT-HASH).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(n: int) -> int:
    a = [1]
    a.append('x')
    return a[1] + 1

if __name__ == "__main__":
    try:
        r = f(0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
