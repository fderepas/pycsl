r"""Test 7793 -- route #490 control (expected PASS): `y = 'a' if n > 0 else 'b'; return y + 'c'` (both arms str) -- a value of one type stays proved.
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(n: int) -> str:
    y = 'a' if n > 0 else 'b'
    return y + 'c'

if __name__ == "__main__":
    try:
        r = f(0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
