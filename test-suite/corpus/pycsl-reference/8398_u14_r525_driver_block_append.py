r"""Test 8398 -- route #525 (expected FAIL: PROVED at base, NOT PROVED: the module literal shortcut is not taken under namespace access): `globals()["OPS"].append("z")` inside the `__main__` driver block before the call; CPython returns 1 (red team 49 probe g1021/ac1023_driver_block_append.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

OPS = ["abc", "defg"]


#@ ensures \result == 0
def f(k: int) -> int:
    for x in OPS:
        if x == "z":
            return 1
    return 0


if __name__ == "__main__":
    try:
        globals()["OPS"].append("z")
        r = f(0)
        print("VIOLATION contract", r) if not (r == 0) else print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
