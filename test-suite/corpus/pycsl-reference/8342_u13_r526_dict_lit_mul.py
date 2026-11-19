r"""Test 8342 -- route #526 (expected FAIL: PROVED at base 1aaa1dfdd, NOT PROVED on the PyCSL-R521 None obligation; red team 49 probe ae1011_dict_lit_mul): `{"a": d.get("k")}["a"] * 3` through a local; CPython TypeError
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
    e = {"a": d.get("k")}
    return e["a"] * 3


if __name__ == "__main__":
    try:
        r = f({})
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
