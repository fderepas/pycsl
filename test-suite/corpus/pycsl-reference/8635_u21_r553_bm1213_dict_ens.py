r"""Test 8635 -- route #553 (expected FAIL: PROVED at base int28, now NOT PROVED on a `PyCSL-R521` obligation; red team 52 probe g1312_bm1213_dict_ens): callee `d["a"] = None` into its `Dict[str, int]` parameter; the caller's `d["a"] + 1`; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ ensures "a" in d
def g(d: Dict[str, int]) -> None:
    d["a"] = None


#@ no_exception \all
def f(k: int, ys: List[int]) -> int:
    d = {"a": 1}
    g(d)
    return d["a"] + 1


if __name__ == "__main__":
    try:
        r = f(1, [1])
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
