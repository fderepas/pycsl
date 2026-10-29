r"""Test 7197 -- route #463 (expected PASS): CONTROL -- a claimed def whose body holds a plain comment, and a `__main__` block with no `#@` line. Every `#@` line is attached; PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ ensures \result == n
def f(n: int) -> int:
    # a plain comment, not a claim
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
