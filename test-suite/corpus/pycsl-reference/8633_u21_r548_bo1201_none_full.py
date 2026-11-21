r"""Test 8633 -- route #548 (expected FAIL: PROVED at base int28, now NOT PROVED on a `PyCSL-R521` obligation; red team 52 probe g1314_bo1201_none_full): `xs[:] = [None, None]`, then `xs[1] + 1`; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def nothing() -> None:
    return None


#@ no_exception \all
def f(d: Dict[str, int], k: str, os_: List[Optional[int]], ys: List[int], o: Optional[int] = None) -> int:
    xs = [1, 2]
    xs[:] = [None, None]
    return xs[1] + 1


if __name__ == "__main__":
    try:
        r = f({}, "a", [None], [1, 2])
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
