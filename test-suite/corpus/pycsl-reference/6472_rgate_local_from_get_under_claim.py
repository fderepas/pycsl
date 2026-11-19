r"""Test 6472 -- route R-gate (expected FAIL): rg-dict-r3 S2 witness w02 (q4) `h`: `v = m.get("a"); s = {v}` under `no_exception \all` (the underivable value through a local). PROVED at base 725a1c7e5; CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict


#@ no_exception \all
#@ ensures \result == 1
def h(m: Dict[str, Any]) -> int:
    v = m.get("a")
    s = {v}
    return 1


if __name__ == "__main__":
    try:
        print(h({"a": [1]}))
    except TypeError:
        print("VIOLATION: TypeError under no_exception \\all")
