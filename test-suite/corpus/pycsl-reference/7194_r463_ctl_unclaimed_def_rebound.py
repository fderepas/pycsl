r"""Test 7194 -- route #463 (expected PASS): CONTROL -- a module-level `def f` bound twice where only the LAST (live) binding is claimed: no claim is shadowed, and the model agrees with CPython that the last def wins. PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass


def f(n: int) -> int:
    return n + 1


#@ ensures \result == n
def f(n: int) -> int:
    return n


if __name__ == "__main__":
    try:
        r = f(1)
        if not (r == 1):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
