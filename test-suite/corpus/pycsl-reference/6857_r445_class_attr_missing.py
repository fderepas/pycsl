r"""Test 6857 -- route #445 (expected FAIL): red team 36 witness `witnesses-r445/c4_n013_class_attr_undef.py` (MEASURED PROVED under `#@ no_exception \all` on main db6c57253): `P.zzz` on a file class object; CPython AttributeError. Refused PYCSL-R445-ATTRIBUTE-NOT-DEFINED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class P:
    k = 1


#@ no_exception \all
def f(a: int) -> int:
    return P.zzz


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
