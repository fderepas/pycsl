r"""Test 8432 -- route #528 (expected FAIL: PROVED at base, NOT PROVED: the PyCSL-R528 piece-index assertion; red team 49 probe al1016): `len(x.split("=")[1])` per element in a loop; CPython IndexError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(xs: List[str]) -> int:
    t = 0
    for x in xs:
        t += len(x.split("=")[1])
    return t


if __name__ == "__main__":
    try:
        r = f(["a=1", "b"])
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
