r"""Test 8387 -- route #523 (expected FAIL: PROVED at base, REFUSED PYCSL-R523-STR-LITERAL-LIST-MUTATED): `a.append("z")` inside a `try`, then `p[2]` under `no_exception \all`; CPython raises IndexError (red team 49 probe g1016/x1040_append_in_try_idx2.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(k: int, s: str) -> int:
    a = ["abc", "defg"]
    try:
        a.append("z")
    except ValueError:
        pass
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
