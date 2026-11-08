r"""Test 8200 -- route #516 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R508-INT-FLOAT-PROMOTION-UNMODELLED; red team 47 probe g819/w8006_IF_k_plus_v_items): `for k, v in d.items(): w = k + v` over `Dict[int, float]`; CPython f({10**400: 0.5}) raises OverflowError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(d: Dict[int, float]) -> int:
    for k, v in d.items():
        w = k + v
    return 1


if __name__ == "__main__":
    try:
        r = f({10**400: 0.5})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
