r"""Test 7201 -- route #464 (expected FAIL): red-team 37 witness `e29_n102_outside_reads_private_classattr` -- `C.__K` outside any class reads `__K`; C binds `_C__K`. CPython raises AttributeError (private name mangling); PROVED at 33f7ac681; now REFUSED by route #445 over the mangled names.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class C:
    __K = 1


#@ no_exception \all
def f(n: int) -> int:
    return C.__K + n


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
