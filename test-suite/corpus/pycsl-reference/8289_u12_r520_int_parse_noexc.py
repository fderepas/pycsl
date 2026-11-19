r"""Test 8289 -- route #520 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 48 probe g923/h9009_int_parse_noexc.py): `field(default_factory=lambda: int("x"))`; the constructor is lowered to a record literal and its body never judged; CPython raises ValueError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import dataclasses


@dataclasses.dataclass
class P:
    a: int = dataclasses.field(default_factory=lambda: int("x"))


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
