r"""Test 7540 -- route #476 (expected FAIL): g34_w103_helper_redefined_after_main -- red-team 39: `g` raises, `f` returns `g(n)` from the `__main__` block, a second `def g` after the guard; PROVED `no_exception \all` at d6abee90b, CPython ZeroDivisionError; now REFUSED (PYCSL-R476-REBOUND-AFTER-FRONTIER).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

def g(x: int) -> int:
    return 1 // (x - x)


#@ no_exception \all
def f(n: int) -> int:
    return g(n)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)


def g(x: int) -> int:
    return x
