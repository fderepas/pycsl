r"""Test 8127 -- route #517 (expected FAIL: PROVED at base, REFUSED PYCSL-R517-TYPE-PARAM-NAME-READ; red team 47 probe a9012_def_tp_bound): `def f[K: int]()`: a bound does not make K an int; CPython returns the TypeVar
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

K = 5


#@ ensures \result == 5
def f[K: int]() -> int:
    return K


if __name__ == "__main__":
    try:
        r = f()
        if r != 5:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
