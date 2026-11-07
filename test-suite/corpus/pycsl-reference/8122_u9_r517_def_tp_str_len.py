r"""Test 8122 -- route #517 (expected FAIL: PROVED at base, REFUSED PYCSL-R517-TYPE-PARAM-NAME-READ; red team 47 probe a9005_def_tp_str_len): `def f[S]()`: `len(S)` read the str constant; CPython raises TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

S = "ab"


#@ no_exception \all
def f[S]() -> int:
    return len(S)


if __name__ == "__main__":
    try:
        r = f()
        if r != 2:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
