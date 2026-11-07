r"""Test 7792 -- route #490 control (expected PASS): `y = None if n == 0 else 1; if y is not None: z = y + 1` -- a value of one type stays proved.
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(n: int) -> int:
    y = None if n == 0 else 1
    z = 0
    if y is not None:
        z = y + 1
    return z

if __name__ == "__main__":
    try:
        r = f(0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
