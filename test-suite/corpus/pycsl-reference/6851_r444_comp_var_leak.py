r"""Test 6851 -- route #444 (expected FAIL): red team 36 witness `witnesses-r444/c1_o150_comp_var_leak.py` (MEASURED PROVED under `#@ no_exception \all` on main db6c57253): a list-comprehension target read after the comprehension (`[x for x in xs]; return x`); CPython NameError. Refused PYCSL-R444-UNBOUND-NAME.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(xs: List[int]) -> int:
    ys = [x for x in xs]
    return x


if __name__ == "__main__":
    try:
        r = f([1])
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
