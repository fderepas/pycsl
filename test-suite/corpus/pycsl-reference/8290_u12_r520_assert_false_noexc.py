r"""Test 8290 -- route #520 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 48 probe g923/h9030_assert_false_noexc.py): `field(default_factory=mk_assert)`, a def doing `assert False`; the constructor is lowered to a record literal and its body never judged; CPython raises AssertionError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import dataclasses


def mk_assert() -> int:
    assert False
    return 0


@dataclasses.dataclass
class P:
    a: int = dataclasses.field(default_factory=mk_assert)


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
