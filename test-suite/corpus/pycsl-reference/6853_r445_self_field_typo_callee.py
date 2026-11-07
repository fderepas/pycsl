r"""Test 6853 -- route #445 (expected FAIL): red team 36 witness `witnesses-r445/c11_q028_field_typo_self.py` (MEASURED PROVED under `#@ no_exception \all` on main db6c57253): `self.cout` (no such field) in a method CALLED by the claiming function; CPython AttributeError. Refused PYCSL-R445-ATTRIBUTE-NOT-DEFINED (the claim reaches the callee).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class P:
    def __init__(self) -> None:
        self.count = 1

    def g(self) -> int:
        return self.cout



#@ no_exception \all
def f(p: P) -> int:
    return p.g()


if __name__ == "__main__":
    try:
        r = f(P())
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
