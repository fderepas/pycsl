r"""Test 7188 -- route #463 (expected FAIL): driver probe (cc1) -- an indented `#@ assert` and a column-0 `#@ assert 1 == 2` at end of file: the indented line turned the end-of-file guard's column-0 test off and the column-0 line was dropped. Measured on 33f7ac681: PROVED; now REFUSED (route #463).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ ensures \result == n
def f(n: int) -> int:
    x = n
    return x
    #@ assert 1 == 1
#@ assert 1 == 2
