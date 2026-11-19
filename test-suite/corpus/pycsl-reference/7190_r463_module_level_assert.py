r"""Test 7190 -- route #463 (expected FAIL): driver probe (cc1) -- `#@ assert x == 2` between module-level statements attaches cleanly but module-level code is never lowered. Measured on 33f7ac681: PROVED; now REFUSED (route #463).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ ensures \result == n
def f(n: int) -> int:
    return n


x = 1
#@ assert x == 2
y = x + 1
