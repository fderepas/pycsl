r"""Test 7815 -- route #495 (expected FAIL: PROVED at base, REFUSED PYCSL-CONTRADICTORY-ASSIGNS): a VERIFIED `__len__` declared `#@ assigns \nothing` + `#@ assigns self.v` writes `self.v`; a `\trusted` k returns `len(o)`; the caller's `ensures \result == 0` over `o.v`; CPython returns 7 (red team 42 probe g312/w3140_two_assigns_contig_len.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class C:
    def __init__(self) -> None:
        self.v = 0

    #@ assigns \nothing
    #@ assigns self.v
    def __len__(self) -> int:
        self.v = 7
        return 1


#@ \trusted
def k(o: C) -> int:
    return len(o)


#@ ensures \result == 0
def f(n: int) -> int:
    o = C()
    k(o)
    return o.v


if __name__ == "__main__":
    try:
        r = f(0)
        if not (r == 0):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
