r"""Test 8631 -- route #548 (expected FAIL: PROVED at base int28, now NOT PROVED on a `PyCSL-R521` obligation; red team 52 probe g1306_bg1243_slice_store_get): `xs[0:1] = [d.get(k)]`, then `xs[0] + 1`; CPython TypeError on f({}, 'a', [1])
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(d: Dict[str, int], k: str, ys: List[int]) -> int:
    xs = [1, 2]
    xs[0:1] = [d.get(k)]
    return xs[0] + 1


if __name__ == "__main__":
    try:
        r = f({}, "a", [1])
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
