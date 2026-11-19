r"""Test 8344 -- route #526 (expected FAIL: PROVED at base 1aaa1dfdd, NOT PROVED on the PyCSL-R521 None obligation; red team 49 probe ae1018_ctor_arg_add): `R(d.get("k")).v + 1` (constructor argument); CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class R:
    v: int


def g(d: Dict[str, int]) -> int:
    return d.get("k")


def h(x: int) -> int:
    return x + 1


#@ no_exception \all
def f(d: Dict[str, int]) -> int:
    r = R(d.get("k"))
    return r.v + 1


if __name__ == "__main__":
    try:
        r = f({})
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
