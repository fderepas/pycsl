r"""Test 8325 -- route #521 (expected FAIL: PROVED at base 1aaa1dfdd, NOT PROVED on the PyCSL-R521 None obligation; red team 49 probe q1005_ss_lit_in_get): membership `"a" in d.get("k")` (haystack None); CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(d: Dict[str, str], s: str) -> int:
    return 1 if "a" in d.get("k") else 0


if __name__ == "__main__":
    try:
        r = f({}, "ab")
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
