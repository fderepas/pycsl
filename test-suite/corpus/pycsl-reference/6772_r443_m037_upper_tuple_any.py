r"""Test 6772 -- route #443 (expected FAIL): red-team 35 probe m037_upper_tuple_any -- a component of `Tuple[Any, ...]` used as a method receiver. PROVED at base fa7cbb1aa under `#@ no_exception \all`; CPython raises AttributeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R443-UNDERIVABLE-RECEIVER-ATTRIBUTE).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(t: Tuple[Any, ...]) -> int:
    return len(t[0].upper())


if __name__ == "__main__":
    try:
        r = f((1,))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
