r"""Test 8327 -- route #521 (expected FAIL: PROVED at base 1aaa1dfdd, NOT PROVED on the PyCSL-R521 None obligation; red team 49 probe af1000_optdict_i_neg): unary `-d["k"]` of Dict[str, Optional[int]]; CPython f({"k": None}) TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ requires "k" in d
#@ no_exception \all
def f(d: Dict[str, Optional[int]]) -> int:
    return -d["k"]


if __name__ == "__main__":
    try:
        r = f({"k": None})
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
