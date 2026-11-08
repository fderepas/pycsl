r"""Test 8602 -- route #543 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R543-ANNOTATED-BINDING-KIND; red team 51 probe g1225/ad1203_dc_int_list_none.py): a `List[P]` local initialised `[None]`; `xs[0].a`; CPython f(1) -> AttributeError 'NoneType' object has no attribute 'a'
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class P:
    a: int



#@ no_exception \all
def f(k: int) -> int:
    xs: List[P] = [None]
    return xs[0].a


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
