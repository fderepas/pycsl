r"""Test 8429 -- route #528 (expected FAIL: PROVED at base, NOT PROVED: the PyCSL-R528 piece-index assertion; red team 49 probe al1000): `s.split(",")[i]` with a parameter index; CPython IndexError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ requires i >= 0
#@ no_exception \all
def f(s: str, i: int) -> int:
    return len(s.split(",")[i])


if __name__ == "__main__":
    try:
        r = f("ab", 1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
