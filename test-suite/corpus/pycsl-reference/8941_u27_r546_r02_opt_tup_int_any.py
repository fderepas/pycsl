r"""Test 8941 -- route #546 residual (expected FAIL: PROVED at base run5-int34 06ad15036, now NOT PROVED on a `PyCSL-R521` obligation; u27 witness r02_opt_tup_int_any): `-> Optional[Tuple[int, Any]]` returning `(None, 1)`; the caller reads `x = t[0]; x + 1`; CPython raises TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass


def g(k: int) -> Optional[Tuple[int, Any]]:
    return (None, 1)


#@ no_exception \all
def f(k: int) -> int:
    t = g(k)
    if t is not None:
        x = t[0]
        return x + 1
    return 0


if __name__ == "__main__":
    try:
        r = f(1)
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
