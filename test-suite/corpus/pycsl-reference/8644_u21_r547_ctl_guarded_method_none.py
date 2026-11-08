r"""Test 8644 -- route #547 (control, expected PASS): `v = Q.m(k); if v is None: return 0; return v + 1` for a `-> int` staticmethod that returns None on one path -- the guarded use stays proved (route #490's narrowing)
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class Q:
    @staticmethod
    def m(k: int) -> int:
        if k > 0:
            return k
        return None  # type: ignore


#@ no_exception \all
def f(k: int) -> int:
    v = Q.m(k)
    if v is None:
        return 0
    return v + 1


if __name__ == "__main__":
    print("result", f(0), f(2))
