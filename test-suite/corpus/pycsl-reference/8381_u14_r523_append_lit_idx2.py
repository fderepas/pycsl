r"""Test 8381 -- route #523 (expected FAIL: PROVED at base, REFUSED PYCSL-R523-STR-LITERAL-LIST-MUTATED): `a.append("z")` then `p[2]` over every element under `no_exception \all`; CPython raises IndexError on 'z' (red team 49 probe g1016/x1000_append_lit_idx2.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(k: int, s: str) -> int:
    a = ["abc", "defg"]
    a.append("z")
    t = 0
    for p in a:
        if p[2] == "q":
            t += 1
    return t


if __name__ == "__main__":
    try:
        r = f(0, "z")
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
