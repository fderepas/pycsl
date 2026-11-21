r"""Test 7541 -- route #476 (expected FAIL): g40_u900_value_redef_after_main -- red-team 39: the contract `\result == n` proved through the LAST `g`, the script runs the first (2 for 1); now REFUSED (PYCSL-R476-REBOUND-AFTER-FRONTIER).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

def g(x: int) -> int:
    return x + 1


#@ ensures \result == n
def f(n: int) -> int:
    return g(n)


if __name__ == "__main__":
    try:
        r = f(1)
        if not (r == 1):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)


def g(x: int) -> int:
    return x
