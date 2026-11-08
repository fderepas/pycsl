r"""Test 8385 -- route #523 (expected FAIL: PROVED at base, REFUSED PYCSL-R523-STR-LITERAL-LIST-MUTATED): a first loop over the literal, `a.append("z")`, a second loop indexing `p[2]` under `no_exception \all`; CPython raises IndexError (red team 49 probe g1018/z1018_str_list_two_loops.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(k: int) -> int:
    a = ["abc", "defg"]
    t = 0
    for p in a:
        t += 1
    a.append("z")
    for p in a:
        if p[2] == "q":
            t += 1
    return t


if __name__ == "__main__":
    try:
        r = f(0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
