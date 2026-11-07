r"""Test 8630 -- route #548 (expected FAIL: PROVED at base int28, now NOT PROVED on a `PyCSL-R521` obligation; red team 52 probe g1301_bb1258_slice_store_none): `xs[0:1] = [None]` into a local int list, then `xs[0] + 1`; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class R:
    a: int


class K:
    a: int = 0


#@ no_exception \all
def f(k: int) -> int:
    xs = [1, 2]
    xs[0:1] = [None]
    return xs[0] + 1


if __name__ == "__main__":
    try:
        r = f(1)
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
