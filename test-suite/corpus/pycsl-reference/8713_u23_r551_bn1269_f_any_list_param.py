r"""Test 8713 -- route #551 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R551-CONSTRUCTOR-ARGUMENT-KIND; red team 52 probe g1313/bn1269_f_any_list_param.py): an `Any` local bound to `["a"]` passed to `xs: List[int]` whose body takes `sum(xs)`; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, xs: List[int]) -> None:
        self.n = sum(xs)


#@ no_exception \all
def f(k: int) -> int:
    v: Any = ["a"]
    c = C(v)
    return 1


if __name__ == "__main__":
    try:
        r = f(1)
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
