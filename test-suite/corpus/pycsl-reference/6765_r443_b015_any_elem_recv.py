r"""Test 6765 -- route #443 (expected FAIL): red-team 35 probe b015_any_elem_recv -- elements of a bare `list` used as a method receiver. PROVED at base fa7cbb1aa under `#@ no_exception \all`; CPython raises AttributeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R443-UNDERIVABLE-RECEIVER-ATTRIBUTE).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(xs: list) -> int:
    return xs[0].bit_length() + len(xs[1].upper())


if __name__ == "__main__":
    try:
        r = f([1, 2])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
