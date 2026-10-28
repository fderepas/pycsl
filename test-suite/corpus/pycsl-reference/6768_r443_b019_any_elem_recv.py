r"""Test 6768 -- route #443 (expected FAIL): red-team 35 probe b019_any_elem_recv -- `d.get('a', '')` over `Dict[str, Any]` used as a method receiver. PROVED at base fa7cbb1aa under `#@ no_exception \all`; CPython raises AttributeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R443-UNDERIVABLE-RECEIVER-ATTRIBUTE).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(d: Dict[str, Any]) -> int:
    return len(d.get("a", "").upper())


if __name__ == "__main__":
    try:
        r = f({"a": 1})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
