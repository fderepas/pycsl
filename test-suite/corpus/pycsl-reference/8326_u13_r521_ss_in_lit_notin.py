r"""Test 8326 -- route #521 (expected FAIL: PROVED at base 1aaa1dfdd, NOT PROVED on the PyCSL-R521 None obligation; red team 49 probe q1004_ss_in_lit_notin): `d.get("k") not in "ab"`; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(d: Dict[str, str], s: str) -> int:
    return 1 if d.get("k") not in "ab" else 0


if __name__ == "__main__":
    try:
        r = f({}, "ab")
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
