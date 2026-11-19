r"""Test 8546 -- route #544 (expected FAIL: PROVED at base, REFUSED PYCSL-R441-BUILTIN-SIGNATURE; red team 51 probe aq1210_field_guard): `if isinstance(r.s, None): return 0`; CPython f(R(..)) raises TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class R:
    s: Optional[str]



#@ no_exception \all
def f(r: R) -> int:
    if isinstance(r.s, None):
        return 0
    return 1


if __name__ == "__main__":
    try:
        r = f(R("a"))
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
