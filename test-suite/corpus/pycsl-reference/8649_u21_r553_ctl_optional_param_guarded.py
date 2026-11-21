r"""Test 8649 -- route #553 (control, expected PASS): the callee annotates `xs: List[Optional[int]]` and stores None; the caller narrows `v = xs[0]; if v is None: return 0`
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ requires len(xs) >= 1
def g(xs: List[Optional[int]]) -> None:
    xs[0] = None


#@ no_exception \all
def f(k: int) -> int:
    xs = [1]
    g(xs)
    v = xs[0]
    if v is None:
        return 0
    return v + 1


if __name__ == "__main__":
    print("result", f(3))
