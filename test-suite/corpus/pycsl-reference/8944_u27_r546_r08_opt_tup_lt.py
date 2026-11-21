r"""Test 8944 -- route #546 residual (expected FAIL: PROVED at base run5-int34 06ad15036, now NOT PROVED on a `PyCSL-R521` obligation; u27 witness r08_opt_tup_lt): `-> Optional[Tuple[Any, int]]` returning `(1, None)`; the caller reads `x = t[1]; x < 3`; CPython raises TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass


def g(k: int) -> Optional[Tuple[Any, int]]:
    return (1, None)


#@ no_exception \all
def f(k: int) -> bool:
    t = g(k)
    if t is not None:
        x = t[1]
        return x < 3
    return False


if __name__ == "__main__":
    try:
        r = f(1)
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
