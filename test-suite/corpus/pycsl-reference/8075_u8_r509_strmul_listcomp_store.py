r"""Test 8075 -- route #509 (expected FAIL, --memory-model store: a Why3 error of the mode at base (`store` does not occur in the expression), now REFUSED by name PYCSL-R509-COMPREHENSION-OVERFLOW-SITE; red team 46 probe y7000_strmul_listcomp): a list comprehension element `"ab" * n`; CPython f(10**20) raises OverflowError
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model store
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(n: int) -> int:
    v = ["ab" * n for _ in range(1)]
    return 1


if __name__ == "__main__":
    try:
        r = f(10**20)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
