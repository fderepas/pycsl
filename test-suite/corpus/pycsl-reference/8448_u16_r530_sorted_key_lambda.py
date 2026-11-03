r"""Test 8448 -- route #530 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 50 probe g1107/bh1083_sorted_key_lambda_add_init.py): `sorted(xs, key=lambda x: x + 1)` of List[str] in a constructor judged by route #519; CPython TypeError: can only concatenate str
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, xs: List[str]) -> None:
        self.k = sorted(xs, key=lambda x: x + 1)


#@ no_exception \all
def f(xs: List[str]) -> int:
    c = C(xs)
    return 1


if __name__ == "__main__":
    try:
        r = f(["a", "b"])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
