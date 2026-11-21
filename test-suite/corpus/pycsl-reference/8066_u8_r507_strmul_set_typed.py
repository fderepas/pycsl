r"""Test 8066 -- route #507 (expected FAIL, --memory-model typed: a Why3 error of the mode at base (`option` unbound in the set preamble), now REFUSED by name PYCSL-R507-OVERFLOW-SITE-UNLOWERED; red team 46 probe n7001_strmul_set): a set display `{"ab" * n}` drops route #414 bound on the repetition count; CPython f(10**20) raises OverflowError
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model typed
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(n: int) -> int:
    zs: List[int] = []
    v = {"ab" * n}
    return 1


if __name__ == "__main__":
    try:
        r = f(10**20)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
