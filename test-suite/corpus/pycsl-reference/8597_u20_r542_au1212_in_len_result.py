r"""Test 8597 -- route #542 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R542-NON-CONTAINER-OPERAND; red team 51 probe g1242/au1212_in_len_result.py): `1 in len(s)`; CPython f("a") -> TypeError argument of type 'int' is not a container or iterable
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(s: str) -> int:
    return 1 if 1 in len(s) else 0


if __name__ == "__main__":
    try:
        r = f("a")
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
