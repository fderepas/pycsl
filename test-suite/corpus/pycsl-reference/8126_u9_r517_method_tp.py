r"""Test 8126 -- route #517 (expected FAIL: PROVED at base, REFUSED PYCSL-R517-TYPE-PARAM-NAME-READ; red team 47 probe a9011_method_tp): `def m[K](self)`: `return K` read the module constant; CPython returns the TypeVar
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

K = 5


class C:
    #@ ensures \result == 5
    def m[K](self) -> int:
        return K


if __name__ == "__main__":
    try:
        r = C().m()
        if r != 5:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
