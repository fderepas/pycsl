r"""Test 6454 -- route #431 (expected FAIL): rg-dict-r3 probe l3q. A `break` in `finally:` inside a loop swallows the ambient hash TypeError of an un-claimed function, so CPython returns 2 while `ensures \result == 1` (FAILED at base 725a1c7e5, fail-closed; the `__main__` driver prints VIOLATION). Now REFUSED before lowering.
"""
# pycsl-expected: FAIL
from typing import Dict, Any


#@ ensures \result == 1
def f(m: Dict[str, Any]) -> int:
    r = 2
    for i in range(1):
        try:
            n = hash(m.get("a"))
            r = 1
        finally:
            break
    return r


if __name__ == "__main__":
    r = f({"a": [1]})
    print("VIOLATION" if r != 1 else "ok", r)
