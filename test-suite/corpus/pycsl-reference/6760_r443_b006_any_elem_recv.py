r"""Test 6760 -- route #443 (expected FAIL): red-team 35 probe b006_any_elem_recv -- a value of `Dict[str, Any]` (`d['a'].upper()`) used as a method receiver. PROVED at base fa7cbb1aa under `#@ no_exception \all`; CPython raises AttributeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R443-UNDERIVABLE-RECEIVER-ATTRIBUTE).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(d: Dict[str, Any]) -> int:
    return len(d["a"].upper())


if __name__ == "__main__":
    try:
        r = f({"a": 1})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
