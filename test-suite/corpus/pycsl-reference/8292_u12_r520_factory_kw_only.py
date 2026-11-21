r"""Test 8292 -- route #520 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 48 probe g924/i9008_factory_kw_only.py): a `kw_only=True` dataclass whose factory reads a missing key; the constructor is lowered to a record literal and its body never judged; CPython raises KeyError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import dataclasses


@dataclasses.dataclass(kw_only=True)
class P:
    a: int = dataclasses.field(default_factory=lambda: {"a": 1}["z"])


#@ no_exception \all
def f() -> int:
    p = P()
    return 1


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
