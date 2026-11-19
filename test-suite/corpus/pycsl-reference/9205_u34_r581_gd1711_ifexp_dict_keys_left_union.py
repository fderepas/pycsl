r"""Test 9205 -- route #581 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R458-OPERAND-CLASSES; red team 55 probe gd1711_ifexp_dict_keys_left_union.py): `x = {} if not c else m.keys()` then `len(x | {"z"})`; CPython TypeError: unsupported operand type(s) for |: 'dict' and 'set'
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(m: Dict[str, str], c: bool) -> int:
    x = {} if not c else m.keys()
    return len(x | {"z"})


if __name__ == "__main__":
    try:
        print("result", repr(f({"a": "x"}, False))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
