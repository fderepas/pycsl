r"""Test 6855 -- route #445 (expected FAIL): red team 36 witness `witnesses-r445/c17_w004_inherited_field_missing.py` (MEASURED PROVED under `#@ no_exception \all` on main db6c57253): a base field read on a subclass whose `__init__` never calls `super().__init__()`; CPython AttributeError. Refused PYCSL-R445-ATTRIBUTE-NOT-DEFINED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class B:
    def __init__(self) -> None:
        self.a = 1


class Q(B):
    def __init__(self) -> None:
        pass

    def g(self) -> int:
        return self.a



#@ no_exception \all
def f(p: Q) -> int:
    return p.g()


if __name__ == "__main__":
    try:
        r = f(Q())
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
