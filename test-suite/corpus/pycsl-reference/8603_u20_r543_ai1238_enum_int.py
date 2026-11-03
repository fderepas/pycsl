r"""Test 8603 -- route #543 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R543-ANNOTATED-BINDING-KIND; red team 51 probe g1230/ai1238_enum_int.py): a local annotated with a one-member enum bound to `5`; `x.value`; CPython f(0) -> AttributeError 'int' object has no attribute 'value'
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import enum


class C(enum.Enum):
    A = 1



#@ no_exception \all
def f(k: int) -> int:
    x: C = 5
    return x.value


if __name__ == "__main__":
    try:
        r = f(0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
