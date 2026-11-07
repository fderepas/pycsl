r"""Test 9200 -- route #581 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R458-OPERAND-CLASSES; red team 55 probe gw1624_setlit_or_L.py): `x = {} if not c else {"q"}` then `len(x | {"z"})`; CPython TypeError: unsupported operand type(s) for |: 'dict' and 'set'
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(m: Dict[str, str], s: Set[str], c: bool) -> int:
    x = {} if not c else {"q"}
    return len(x | {"z"})


if __name__ == "__main__":
    try:
        print("result", repr(f({"a": "x"}, {"q"}, False))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
