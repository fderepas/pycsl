r"""Test 6773 -- route #443 (expected FAIL): red-team 35 probe m038_upper_bare_list -- an element of a bare `list` used as a method receiver. PROVED at base fa7cbb1aa under `#@ no_exception \all`; CPython raises AttributeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R443-UNDERIVABLE-RECEIVER-ATTRIBUTE).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(xs: list) -> int:
    return len(xs[0].upper())


if __name__ == "__main__":
    try:
        r = f([1])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
