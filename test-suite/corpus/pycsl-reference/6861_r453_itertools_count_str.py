r"""Test 6861 -- route #453 (expected FAIL): red team 36 witness `witnesses-r453/c16_m022_realistic_counter.py` (MEASURED PROVED under `#@ no_exception \all` on main db6c57253): `itertools.count(<str>)` admitted by its tail `count`; CPython TypeError. Refused PYCSL-R453-MODULE-FUNCTION-NOT-ADMITTED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

import itertools



#@ no_exception \all
def f(start: str) -> int:
    c = itertools.count(start)
    return 1


if __name__ == "__main__":
    try:
        r = f('0')
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
