r"""Test 8115 -- route #510 (expected FAIL: PROVED at base, REFUSED PYCSL-R510-TYPE-STATEMENT-NAME-READ; red team 47 probe r8019_branch): `type x = int` in one branch rebinds the local x; CPython f(True) returns the TypeAliasType
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ ensures \result == 5
def f(c: bool) -> int:
    x = 5
    if c:
        type x = int
    return x


if __name__ == "__main__":
    try:
        r = f(True)
        if r != 5:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
