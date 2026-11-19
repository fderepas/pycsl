r"""Test 8601 -- route #543 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R543-ANNOTATED-BINDING-KIND; red team 51 probe g1225/ad1200_dc_int_none_field.py): a local annotated with a one-int-field dataclass bound to `None`; `x.a`; CPython f(1) -> AttributeError 'NoneType' object has no attribute 'a'
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class P:
    a: int



#@ no_exception \all
def f(k: int) -> int:
    x: P = None
    return x.a


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
