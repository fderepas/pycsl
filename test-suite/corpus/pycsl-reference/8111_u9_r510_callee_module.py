r"""Test 8111 -- route #510 (expected FAIL: PROVED at base, REFUSED PYCSL-R510-TYPE-STATEMENT-NAME-READ; red team 47 probe r8010_callee_module_noexc): a module-level `type g = int` after `def g` rebinds the callee; CPython f(1) raises TypeError (not callable)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def g(n: int) -> int:
    return n


#@ no_exception \all
def f(n: int) -> int:
    return g(n) + 1


type g = int


if __name__ == "__main__":
    try:
        r = f(1)
        if r != 2:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
