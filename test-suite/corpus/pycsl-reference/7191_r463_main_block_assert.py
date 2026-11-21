r"""Test 7191 -- route #463 (expected FAIL): driver probe (cc1) -- `#@ assert x == 2` inside `if __name__ == "__main__":` is never lowered. Measured on 33f7ac681: PROVED; now REFUSED (route #463).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ ensures \result == n
def f(n: int) -> int:
    return n


if __name__ == "__main__":
    x = f(1)
    #@ assert x == 2
    print(x)
