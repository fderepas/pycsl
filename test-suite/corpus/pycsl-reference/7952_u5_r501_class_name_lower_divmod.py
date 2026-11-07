r"""Test 7952 -- route #501 (expected FAIL: PROVED at base, REFUSED PYCSL-R496-CALLEE-UNLISTED-CALL): g's free `divmod(5, n)`; a class is named `Divmod`; f catches ZeroDivisionError; CPython returns 2 (red team 45 probe g600/a60003_class_name_lower_divmod.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class Divmod:
    def __init__(self) -> None:
        self.v = 0


#@ ensures \result == 1
def g(n: int) -> int:
    q = divmod(5, n)
    return 1


#@ ensures \result == 1
def f(n: int) -> int:
    try:
        return g(n)
    except ZeroDivisionError:
        return 2


if __name__ == "__main__":
    try:
        r = f(0)
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
