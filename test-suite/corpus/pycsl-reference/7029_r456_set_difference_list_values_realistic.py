r"""Test 7029 -- route #456 (expected FAIL): red-team 36 probe c22_v015_realistic -- `tags.difference(groups.values())` with `groups: Dict[str, List[str]]` (CPython TypeError). PROVED at base 8fe7204c3 under `#@ no_exception \all`; now REFUSED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(tags: Set[str], groups: Dict[str, List[str]]) -> int:
    rest = tags.difference(groups.values())
    return len(rest)


if __name__ == "__main__":
    try:
        r = f({'a'}, {'g': ['a']})
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
