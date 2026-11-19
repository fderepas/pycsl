r"""Test 8943 -- route #546 residual (expected FAIL: PROVED at base run5-int34 06ad15036, now NOT PROVED on a `PyCSL-R521` obligation; u27 witness r07_opt_tup_get): `-> Optional[Tuple[Any, int]]` returning `(1, d.get(k))`; the caller reads `x = t[1]; x + 1`; CPython raises TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass


def g(d: Dict[str, int], k: str) -> Optional[Tuple[Any, int]]:
    return (1, d.get(k))


#@ no_exception \all
def f(d: Dict[str, int], k: str) -> int:
    t = g(d, k)
    if t is not None:
        x = t[1]
        return x + 1
    return 0


if __name__ == "__main__":
    try:
        r = f({}, 'a')
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
