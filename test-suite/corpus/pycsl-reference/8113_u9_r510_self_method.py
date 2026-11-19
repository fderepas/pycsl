r"""Test 8113 -- route #510 (expected FAIL: PROVED at base, REFUSED PYCSL-R510-TYPE-STATEMENT-NAME-READ; red team 47 probe r8015_self_field_method): `type self = int` in a method, then `self.v`; CPython raises AttributeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class P:
    def __init__(self, v: int) -> None:
        self.v = v

    #@ no_exception \all
    def m(self) -> int:
        type self = int
        return self.v


if __name__ == "__main__":
    try:
        r = P(1).m()
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
