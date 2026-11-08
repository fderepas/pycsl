r"""Test 8450 -- route #531 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R315-UNMODELLED-CONSTRUCTOR; red team 50 probe g1101/bb1070_init_reads_unset_field.py): `self.k = self.j + n` before `self.j` is stored in a constructor judged by route #519; CPython AttributeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, n: int) -> None:
        self.k = self.j + n
        self.j = 1


#@ no_exception \all
def f(n: int) -> int:
    c = C(n)
    return 1


if __name__ == "__main__":
    try:
        r = f(5)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
