r"""Test 6780 -- route #442 (expected PASS): CONTROL -- `isinstance(x, str)` (a builtin class NoneType does not subclass, never rebound in the file) narrows `Optional[str]`; PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union


#@ no_exception \all
def f(x: Optional[str]) -> int:
    if isinstance(x, str):
        return len(x.upper())
    return 0


if __name__ == "__main__":
    try:
        r = f(None)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
