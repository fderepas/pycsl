r"""Test 8110 -- route #510 (expected FAIL: PROVED at base, REFUSED PYCSL-R510-TYPE-STATEMENT-NAME-READ; red team 47 probe r8008_loopvar_use): `type i = int` rebinds the loop variable, then `k += i`; CPython raises TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f() -> int:
    k = 0
    for i in range(3):
        type i = int
        k += i
    return k


if __name__ == "__main__":
    try:
        r = f()
        if r != 3:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
