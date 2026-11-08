r"""Test 8382 -- route #523 (expected FAIL: PROVED at base, REFUSED PYCSL-R523-STR-LITERAL-LIST-MUTATED): `a.append(None)` then `t += len(p)` under `no_exception \all`; CPython raises TypeError (red team 49 probe g1016/x1001_append_lit_len_none.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(k: int, s: str) -> int:
    a = ["abc", "defg"]
    a.append(None)
    t = 0
    for p in a:
        t += len(p)
    return t


if __name__ == "__main__":
    try:
        r = f(0, "z")
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
