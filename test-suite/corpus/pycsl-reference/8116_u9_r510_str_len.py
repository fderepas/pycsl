r"""Test 8116 -- route #510 (expected FAIL: PROVED at base, REFUSED PYCSL-R510-TYPE-STATEMENT-NAME-READ; red team 47 probe e8032_strS_type_alias): `len(S)` over the str constant `S = "a"` rebound by `type S = int`; CPython raises TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import sys

S = "a"


#@ ensures \result == 1
#@ no_exception \all
def f() -> int:
    return len(S)


type S = int


if __name__ == "__main__":
    try:
        r = f()
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
