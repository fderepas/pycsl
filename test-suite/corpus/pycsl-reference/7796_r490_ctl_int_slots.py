r"""Test 7796 -- route #490 control (expected PASS): `g(1)` for `g(x: int)`, `x: int = 3` -- a value of one type stays proved.
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

def g(x: int) -> int:
    return x + 1


#@ ensures \result == 5
#@ no_exception \all
def f(n: int) -> int:
    x: int = 3
    return g(x) + 1

if __name__ == "__main__":
    try:
        r = f(0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
