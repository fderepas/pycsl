r"""Test 8380 -- route #523 (expected FAIL: PROVED at base, REFUSED PYCSL-R523-STR-LITERAL-LIST-MUTATED): a local str list literal, `a.append("z")`, then `for p in a: if p == "z": return 1` under `ensures \result == 0`; CPython returns 1 (red team 49 probe g1016/x1076_ens_early_return.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ ensures \result == 0
def f(k: int) -> int:
    a = ["abc", "defg"]
    a.append("z")
    for p in a:
        if p == "z":
            return 1
    return 0


if __name__ == "__main__":
    try:
        r = f(0)
        if not (r == 0):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
