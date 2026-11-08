r"""Test 7542 -- route #476 (expected FAIL): g40_u905_transitive_callee_redef -- red-team 39: `f -> k -> g`, `g` rebound after the guard; PROVED at d6abee90b, CPython ZeroDivisionError; now REFUSED (PYCSL-R476-REBOUND-AFTER-FRONTIER).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

def g(x: int) -> int:
    return 1 // (x - x)


def k(x: int) -> int:
    return g(x)


#@ no_exception \all
def f(n: int) -> int:
    return k(n)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)


def g(x: int) -> int:
    return x
