r"""Test 8648 -- route #553 (control, expected PASS): the callee stores an int into its `List[int]` parameter; the caller reads `xs[0] + 1`
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ requires len(xs) >= 1
#@ requires 0 <= v <= 1000
def g(xs: List[int], v: int) -> None:
    xs[0] = v


#@ requires 0 <= k <= 1000
#@ no_exception \all
def f(k: int) -> int:
    xs = [1]
    g(xs, k)
    return xs[0] + 1


if __name__ == "__main__":
    print("result", f(3))
