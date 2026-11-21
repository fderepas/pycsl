r"""Test 7193 -- route #463 (expected FAIL): driver probe (cc1) -- `#\t@requires n > 0` (hash, tab, at) is a near-miss spelling. Measured on 33f7ac681: the precondition was silently absent, so the run FAILED on `f(0)` with no hint that `n > 0` had been written; now REFUSED (route #463) naming the spelling.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#	@requires n > 0
#@ ensures \result > 0
def f(n: int) -> int:
    return n


if __name__ == "__main__":
    try:
        r = f(0)
        if not (r > 0):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
