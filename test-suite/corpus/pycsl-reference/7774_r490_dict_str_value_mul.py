r"""Test 7774 -- route #490 (expected FAIL): red-team 41 probe x129022_dict_value_mul_int sibling -- `d = {'a': 1, 'b': 'x'}; y = d['b']; y - 2` (CPython TypeError) PROVED (or is the same hashed-literal channel) at base 394a1654a; now REFUSED (PYCSL-R490-LITERAL-INT-HASH).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ ensures \result == 0
#@ no_exception \all
def f(n: int) -> int:
    d = {'a': 1, 'b': 'x'}
    y = d['b']
    z = y - 2
    return 0

if __name__ == "__main__":
    try:
        r = f(0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
