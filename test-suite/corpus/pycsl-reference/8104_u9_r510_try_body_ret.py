r"""Test 8104 -- route #510 (expected FAIL: PROVED at base, REFUSED PYCSL-R510-TYPE-STATEMENT-NAME-READ; red team 47 probe o8032_try_ret): the `type K = int` in a `try` body; CPython returns the TypeAliasType
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

K = 5


#@ ensures \result == 5
def f() -> int:
    return K

try:
    type K = int
except Exception:
    pass


if __name__ == "__main__":
    try:
        r = f()
        if r != 5:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
