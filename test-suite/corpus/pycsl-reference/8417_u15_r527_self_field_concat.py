r"""Test 8417 -- route #527 (expected FAIL: PROVED at base, REFUSED PYCSL-R527-OPTIONAL-OPERAND; red team 49 probe ah1119): `self.s + "x"` with `self.s: Optional[str] = None` in `__init__`; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class K:
    def __init__(self) -> None:
        self.s: Optional[str] = None

    #@ no_exception \all
    def m(self) -> int:
        w = self.s + "x"
        return 1


if __name__ == "__main__":
    try:
        r = K().m()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
