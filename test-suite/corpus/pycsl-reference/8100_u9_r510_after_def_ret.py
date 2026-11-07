r"""Test 8100 -- route #510 (expected FAIL: PROVED at base, REFUSED PYCSL-R510-TYPE-STATEMENT-NAME-READ; red team 47 probe o8000_after_ret): a module-level `type K = int` AFTER the def rebinds the folded constant `K = 5`; `return K` proved `\result == 5`, CPython returns the TypeAliasType K
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

K = 5


#@ ensures \result == 5
def f() -> int:
    return K

type K = int


if __name__ == "__main__":
    try:
        r = f()
        if r != 5:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
