r"""Test 7954 -- route #501 (expected FAIL: PROVED at base, REFUSED PYCSL-R496-CALLEE-UNLISTED-CALL): g's `"{x}".format(n)`; a class K defines a method `format`; f catches KeyError; CPython returns 2 (red team 45 probe g600/a60005_method_named_format.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class K:
    #@ ensures \result == 0
    def format(self) -> int:
        return 0


#@ ensures \result == 1
def g(n: int) -> int:
    y = "{x}".format(n)
    return 1


#@ ensures \result == 1
def f(n: int) -> int:
    try:
        return g(n)
    except KeyError:
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
