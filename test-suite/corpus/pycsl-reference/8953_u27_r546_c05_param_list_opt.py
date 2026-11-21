r"""Test 8953 -- route #546 residual (control, expected PASS; u27 c05_param_list_opt): `h([None, 1])` into `xs: List[Optional[int]]` (the parameter admits None at depth 1); the callee guards each element
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass


#@ no_exception \all
def h(xs: List[Optional[int]]) -> int:
    n = 0
    for x in xs:
        if x is not None:
            n = n + 1
    return n


#@ no_exception \all
def f(k: int) -> int:
    return h([None, 1])


if __name__ == "__main__":
    print("result", f(3))
