r"""Test 8293 -- route #520 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 48 probe g924/i9007_factory_in_ctor_arg.py): `P(Q())`, a field argument whose dataclass factory reads `[1][3]`; the constructor is lowered to a record literal and its body never judged; CPython raises IndexError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import dataclasses


@dataclasses.dataclass
class Q:
    v: int = dataclasses.field(default_factory=lambda: [1][3])


@dataclasses.dataclass
class P:
    q: Q


#@ no_exception \all
def f() -> int:
    p = P(Q())
    return 1


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
