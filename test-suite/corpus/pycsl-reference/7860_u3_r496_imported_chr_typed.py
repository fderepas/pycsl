r"""Test 7860 -- route #496 (expected FAIL: PROVED at base, REFUSED PYCSL-R496-CALLEE-UNLISTED-CALL (typed model)): an IMPORTED g (multi_file_lib/u3_h496b.py) holding `chr(n)`, typed model; f catches ValueError; CPython f(-1) returns 2 (red team 44 probe g514/c51404_chr_import.py)
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model typed
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

from multi_file_lib.u3_h496b import g


#@ ensures \result == 1
def f(n: int) -> int:
    try:
        return g(n)
    except ValueError:
        return 2


if __name__ == "__main__":
    try:
        r = f(-1)
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
