r"""Test 8544 -- route #544 (expected FAIL: PROVED at base, REFUSED PYCSL-R441-BUILTIN-SIGNATURE; red team 51 probe ap1200_isinstance_none): `isinstance(k, None)`; CPython f(1) raises TypeError (isinstance() arg 2 must be a type, a tuple of types, or a union)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(k: int) -> int:
    return 1 if isinstance(k, None) else 0


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
