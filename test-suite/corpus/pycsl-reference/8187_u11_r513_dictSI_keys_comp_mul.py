r"""Test 8187 -- route #513 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R509-COMPREHENSION-OVERFLOW-SITE; red team 47 probe g809/l8024_dictSI_keys_comp_mul_n): `[k * n for k in d]` over `Dict[str, int]`: str keys read as int, the repetition admitted; CPython f({"ab": 1}, 10**20) raises OverflowError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(d: Dict[str, int], n: int) -> int:
    v = [k * n for k in d]
    return 1


if __name__ == "__main__":
    try:
        r = f({"ab": 1}, 10**20)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
