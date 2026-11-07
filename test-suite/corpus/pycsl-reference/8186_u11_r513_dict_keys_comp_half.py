r"""Test 8186 -- route #513 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R508-INT-FLOAT-PROMOTION-UNMODELLED; red team 47 probe g809/l8021_dictIF_keys_comp_mul_half): `[k * 0.5 for k in d]` over `Dict[int, float]`: the keys were read at the LAST type argument (float); CPython f({10**400: 0.5}) raises OverflowError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(d: Dict[int, float]) -> int:
    v = [k * 0.5 for k in d]
    return 1


if __name__ == "__main__":
    try:
        r = f({10**400: 0.5})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
