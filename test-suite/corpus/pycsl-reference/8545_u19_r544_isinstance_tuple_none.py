r"""Test 8545 -- route #544 (expected FAIL: PROVED at base, REFUSED PYCSL-R441-BUILTIN-SIGNATURE; red team 51 probe aq1204_tuple_none_int): `isinstance(k, (None, int))`; CPython f(1) raises TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class R:
    s: Optional[str]



#@ no_exception \all
def f(k: int) -> int:
    return 1 if isinstance(k, (None, int)) else 0


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
