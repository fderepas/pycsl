r"""Test 7781 -- route #490 (expected FAIL): red-team 41 probe w13429_ternary_str_hash_eq -- `y = 5 if n else 'a'; 1 if y > 5 else 0` (CPython TypeError) PROVED (or is the same hashed-literal channel) at base 394a1654a; now REFUSED (PYCSL-R490-LITERAL-INT-HASH).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ requires n == 0
#@ no_exception \all
def f(n: int) -> int:
    y = 5 if n else 'a'
    return 1 if y > 5 else 0

if __name__ == "__main__":
    try:
        r = f(0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
