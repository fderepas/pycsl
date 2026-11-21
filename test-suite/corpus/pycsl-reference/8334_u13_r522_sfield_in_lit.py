r"""Test 8334 -- route #522 (expected FAIL: PROVED at base 1aaa1dfdd, NOT PROVED on the PyCSL-R521 None obligation; red team 49 probe u1027_sfield_in_lit): `r.d.get("k") in "ab"` on a Dict[str, str] field; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class S:
    d: Dict[str, str]


#@ no_exception \all
def f(r: S) -> int:
    return 1 if r.d.get("k") in "ab" else 0


if __name__ == "__main__":
    try:
        r = f(S({}))
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
