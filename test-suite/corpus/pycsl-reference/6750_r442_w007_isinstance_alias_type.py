r"""Test 6750 -- route #442 (expected FAIL): red-team 35 probe w007_isinstance_alias_type -- isinstance narrowing by a class expression that is not RESOLVED to concrete classes none of which NoneType subclasses (`T = object` alias). PROVED at base fa7cbb1aa under `#@ no_exception \all`; CPython raises AttributeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R432-OPTIONAL-RECEIVER-ATTRIBUTE: the guard no longer narrows).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union

T = object


#@ no_exception \all
def f(x: Optional[str]) -> int:
    if isinstance(x, T):
        return len(x.upper())
    return 0


if __name__ == "__main__":
    try:
        r = f(None)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
