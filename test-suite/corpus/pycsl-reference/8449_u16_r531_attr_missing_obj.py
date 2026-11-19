r"""Test 8449 -- route #531 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 50 probe g1100/ba1047_attr_missing_obj.py): `o.nope` of an object parameter in a constructor judged by route #519; CPython AttributeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, o: object) -> None:
        self.k = o.nope


#@ no_exception \all
def f(o: object) -> int:
    c = C(o)
    return 1


if __name__ == "__main__":
    try:
        r = f(object())
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
