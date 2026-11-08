r"""Test 8183 -- route #512 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R509-COMPREHENSION-OVERFLOW-SITE; red team 47 probe g810/m8065_bytesbig256_dictcomp): `{k: bytes([n]) for k in ["a"]}`: an element outside 0..255 in a dict comprehension; CPython f(256) raises ValueError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(n: int) -> int:
    v = {k: bytes([n]) for k in ["a"]}
    return 1


if __name__ == "__main__":
    try:
        r = f(256)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
