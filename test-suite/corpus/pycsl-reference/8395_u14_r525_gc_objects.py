r"""Test 8395 -- route #525 (expected FAIL: PROVED at base, NOT PROVED: the module literal shortcut is not taken under namespace access): `gc.get_objects()` finds the list and appends 'z'; CPython returns 1 (red team 49 probe g1019/aa1024_gc_before_ret.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

OPS = ["abc", "defg"]
import gc
for _o in gc.get_objects():
    if isinstance(_o, list) and _o == ["abc", "defg"]:
        _o.append("z")


#@ ensures \result == 0
def f(k: int) -> int:
    for x in OPS:
        if x == "z":
            return 1
    return 0


if __name__ == "__main__":
    try:
        r = f(0)
        print("VIOLATION contract", r) if r != 0 else print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
