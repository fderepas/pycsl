r"""Test 7778 -- route #490 (expected FAIL): red-team 41 probe s13110_ternary_return -- a helper `-> int` returning `1 if n > 0 else 'a'`, `h(n) + 1` (CPython TypeError) PROVED (or is the same hashed-literal channel) at base 394a1654a; now REFUSED (PYCSL-R490-LITERAL-INT-HASH).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

def h(n: int) -> int:
    return 1 if n > 0 else 'a'


#@ no_exception \all
def f(n: int) -> int:
    return h(n) + 1

if __name__ == "__main__":
    try:
        r = f(0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
