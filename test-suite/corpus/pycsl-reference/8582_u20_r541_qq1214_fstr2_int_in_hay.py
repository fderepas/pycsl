r"""Test 8582 -- route #541 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R542-NON-CONTAINER-OPERAND (the element `p` of the display is a number once `k` is stored); red team 51 probe g1213/qq1214_fstr2_int_in_hay.py): a str-display list takes `.append(k)`; `"a" in p` of the element; CPython f(3) -> TypeError argument of type 'int' is not a container or iterable
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(k: int) -> int:
    a = ["abc", f"defg"]
    a.append(k)
    n = 0
    for p in a:
        if "a" in p:
            n += 1
    return n


if __name__ == "__main__":
    try:
        r = f(3)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
