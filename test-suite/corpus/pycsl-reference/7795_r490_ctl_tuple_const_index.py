r"""Test 7795 -- route #490 control (expected PASS): `t = (1, 'a'); t[0] + 1` (a tuple position keeps its own type) -- a value of one type stays proved.
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ ensures \result == 2
#@ no_exception \all
def f(n: int) -> int:
    t = (1, 'a')
    return t[0] + 1

if __name__ == "__main__":
    try:
        r = f(0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
