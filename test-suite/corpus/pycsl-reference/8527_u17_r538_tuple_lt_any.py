r"""Test 8527 -- route #538 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R538-UNORDERED-TUPLE-COMPARISON; red team 50 probe g1105/bf1047_tuple_lt_any.py): `t < u` of two `Tuple[int, Any]` parameters; CPython `(1, "a") < (1, 2)` TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(t: Tuple[int, Any], u: Tuple[int, Any]) -> int:
    return 1 if t < u else 0


if __name__ == "__main__":
    try:
        r = f((1, "a"), (1, 2))
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
