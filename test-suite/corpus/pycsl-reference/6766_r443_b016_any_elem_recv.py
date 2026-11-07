r"""Test 6766 -- route #443 (expected FAIL): red-team 35 probe b016_any_elem_recv -- an element of `List[List[Any]]` used as a method receiver. PROVED at base fa7cbb1aa under `#@ no_exception \all`; CPython raises AttributeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R443-UNDERIVABLE-RECEIVER-ATTRIBUTE).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(xs: List[List[Any]]) -> int:
    return len(xs[0][0].upper())


if __name__ == "__main__":
    try:
        r = f([[1]])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
