r"""Test 7543 -- route #476 (expected FAIL): g40_u902_reversed_main_guard -- red-team 39: the reversed guard `'__main__' == __name__`; PROVED at d6abee90b, CPython ZeroDivisionError; now REFUSED (PYCSL-R476-REBOUND-AFTER-FRONTIER).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

def g(x: int) -> int:
    return 1 // (x - x)


#@ no_exception \all
def f(n: int) -> int:
    return g(n)


if '__main__' == __name__:
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)


def g(x: int) -> int:
    return x
