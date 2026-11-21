r"""Test 6769 -- route #443 (expected FAIL): red-team 35 probe b020_any_elem_recv -- a `for` target over `Dict[str, Any].values()` in a generator used as a method receiver. PROVED at base fa7cbb1aa under `#@ no_exception \all`; CPython raises AttributeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R443-UNDERIVABLE-RECEIVER-ATTRIBUTE).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(d: Dict[str, Any]) -> int:
    return sum(len(v.upper()) for v in d.values())


if __name__ == "__main__":
    try:
        r = f({"a": 1})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
