r"""Test 8109 -- route #510 (expected FAIL: PROVED at base, REFUSED PYCSL-R510-TYPE-STATEMENT-NAME-READ; red team 47 probe r8006_param_list_idx): `type xs = int` rebinds a list parameter, then `xs[0]`; CPython raises TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ requires len(xs) >= 1
#@ no_exception \all
def f(xs: List[int]) -> int:
    type xs = int
    return xs[0]


if __name__ == "__main__":
    try:
        r = f([1])
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
