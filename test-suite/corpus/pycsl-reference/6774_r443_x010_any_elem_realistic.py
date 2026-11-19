r"""Test 6774 -- route #443 (expected FAIL): red-team 35 probe x010_any_elem_realistic -- `row: List[Any]`; `row[0].strip()` (realistic) used as a method receiver. PROVED at base fa7cbb1aa under `#@ no_exception \all`; CPython raises AttributeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R443-UNDERIVABLE-RECEIVER-ATTRIBUTE).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(row: List[Any]) -> int:
    return len(row[0].strip()) if len(row) > 0 else 0


if __name__ == "__main__":
    try:
        r = f([42])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
