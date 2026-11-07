r"""Test 9201 -- route #581 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R458-OPERAND-CLASSES; red team 55 probe gd1661_ifexp_set_call_left_union.py): `x = {} if not c else set()` then `len(x | {"z"})`; CPython TypeError: unsupported operand type(s) for |: 'dict' and 'set'
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(m: Dict[str, str], c: bool) -> int:
    x = {} if not c else set()
    return len(x | {"z"})


if __name__ == "__main__":
    try:
        print("result", repr(f({"a": "x"}, False))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
