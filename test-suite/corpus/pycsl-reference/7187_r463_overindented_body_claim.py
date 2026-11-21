r"""Test 7187 -- route #463 (expected FAIL): driver probe (cc1) -- an `#@ assert` indented deeper than the statement after it, inside a body, became an unemitted footer. Measured on 33f7ac681: PROVED (`x == n + 1` never checked); now REFUSED (route #463).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ ensures \result == n
def f(n: int) -> int:
    x = n
        #@ assert x == n + 1
    return x


if __name__ == "__main__":
    try:
        r = f(1)
        if not (r == 1):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
