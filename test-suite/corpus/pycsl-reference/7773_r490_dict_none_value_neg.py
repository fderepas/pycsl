r"""Test 7773 -- route #490 (expected FAIL): red-team 41 probe x129124_dict_value_none_neg -- `-{'a': 1, 'b': None}['b']` (CPython TypeError) PROVED (or is the same hashed-literal channel) at base 394a1654a; now REFUSED (PYCSL-R490-LITERAL-INT-HASH).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(n: int) -> int:
    d = {'a': 1, 'b': None}
    z = -d['b']
    return 0

if __name__ == "__main__":
    try:
        r = f(0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
