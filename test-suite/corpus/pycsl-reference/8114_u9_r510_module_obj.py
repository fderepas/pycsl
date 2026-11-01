r"""Test 8114 -- route #510 (expected FAIL: PROVED at base, REFUSED PYCSL-R510-TYPE-STATEMENT-NAME-READ; red team 47 probe r8017_module_global_obj): `type g = int` rebinds a module object, then `g.v`; CPython raises AttributeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self) -> None:
        self.v = 1


g = C()


#@ no_exception \all
def f() -> int:
    return g.v


type g = int


if __name__ == "__main__":
    try:
        r = f()
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
