r"""Test 8430 -- route #528 (expected FAIL: PROVED at base, NOT PROVED: the PyCSL-R528 piece-index assertion; red team 49 probe al1002): `s.split(",")[-2]`; CPython IndexError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(s: str) -> int:
    return len(s.split(",")[-2])


if __name__ == "__main__":
    try:
        r = f("ab")
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
