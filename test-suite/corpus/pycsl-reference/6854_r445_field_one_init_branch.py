r"""Test 6854 -- route #445 (expected FAIL): red team 36 witness `witnesses-r445/c26_a005_field_set_in_branch_init.py` (MEASURED PROVED under `#@ no_exception \all` on main db6c57253): a field stored in only one branch of `__init__`, read by a called method; CPython AttributeError. Refused PYCSL-R445-ATTRIBUTE-NOT-DEFINED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class P:
    def __init__(self, n: int) -> None:
        if n > 0:
            self.x = 1

    def g(self) -> int:
        return self.x



#@ no_exception \all
def f(n: int) -> int:
    return P(n).g()


if __name__ == "__main__":
    try:
        r = f(0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
