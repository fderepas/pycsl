r"""Test 7797 -- route #490 control (expected PASS): `v = h(n); if v is None: return 0; return v + 1` for `def h(n: int) -> int` returning None on one path -- the guarded use stays proved.
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

def h(n: int) -> int:
    if n > 0:
        return n
    return None  # type: ignore


#@ no_exception \all
def f(n: int) -> int:
    v = h(n)
    if v is None:
        return 0
    return v + 1


if __name__ == "__main__":
    try:
        r = f(0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
