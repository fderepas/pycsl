r"""Test 7787 -- route #490 (expected FAIL): route #490 sibling -- `h() + 1` for `def h() -> int: return None` (CPython TypeError) PROVED at base 394a1654a; now REFUSED (PYCSL-R490-LITERAL-INT-HASH): a call of a number-annotated function that returns None is number-or-None at the caller.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

def h() -> int:
    return None  # type: ignore


#@ no_exception \all
def f(n: int) -> int:
    return h() + 1


if __name__ == "__main__":
    try:
        r = f(0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
