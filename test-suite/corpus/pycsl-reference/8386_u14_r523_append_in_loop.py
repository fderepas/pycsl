r"""Test 8386 -- route #523 (expected FAIL: PROVED at base, REFUSED PYCSL-R523-STR-LITERAL-LIST-MUTATED): `a.append("z")` inside a preceding loop, then `p[2]` under `no_exception \all`; CPython raises IndexError (red team 49 probe g1016/x1032_append_in_loop_idx2.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(k: int, s: str) -> int:
    a = ["abc", "defg"]
    for _i in range(1):
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
