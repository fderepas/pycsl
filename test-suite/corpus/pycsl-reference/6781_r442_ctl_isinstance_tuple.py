r"""Test 6781 -- route #442 (expected PASS): CONTROL -- `isinstance(x, (str, bytes))` (a literal tuple of resolved builtin classes) narrows; PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union


#@ no_exception \all
def f(x: Optional[str]) -> int:
    if isinstance(x, (str, bytes)):
        return len(x.upper())
    return 0


if __name__ == "__main__":
    try:
        r = f(None)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
