r"""Test 8331 -- route #522 (expected FAIL: PROVED at base 1aaa1dfdd, NOT PROVED on the PyCSL-R521 None obligation; red team 49 probe u1118_self_add): `self.d.get("k") + 1` in a method; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self) -> None:
        self.d: Dict[str, int] = {}

    #@ no_exception \all
    def m(self) -> int:
        return self.d.get("k") + 1


if __name__ == "__main__":
    try:
        r = C().m()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
