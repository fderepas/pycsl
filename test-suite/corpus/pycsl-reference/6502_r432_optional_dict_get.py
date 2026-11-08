r"""Test 6502 -- route #432 (expected FAIL): `.get` on `Optional[Dict[str, int]]` under `#@ no_exception \all`. PROVED at base 1c083dcbe (= 78b519f63 emission); CPython raises AttributeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R432-OPTIONAL-RECEIVER-ATTRIBUTE).
"""
# pycsl-expected: FAIL
from typing import Optional
from typing import Dict

#@ no_exception \all
def f(d: Optional[Dict[str, int]]) -> int:
    return d.get("a", 0)


if __name__ == "__main__":
    try:
        r = f(None)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
