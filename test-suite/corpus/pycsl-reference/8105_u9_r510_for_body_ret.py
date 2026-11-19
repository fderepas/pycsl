r"""Test 8105 -- route #510 (expected FAIL: PROVED at base, REFUSED PYCSL-R510-TYPE-STATEMENT-NAME-READ; red team 47 probe o8040_for_body_ret): the `type K = int` in a `for` body; CPython returns the TypeAliasType
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

K = 5


#@ ensures \result == 5
def f() -> int:
    return K

for _i in range(1):
    type K = int


if __name__ == "__main__":
    try:
        r = f()
        if r != 5:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
