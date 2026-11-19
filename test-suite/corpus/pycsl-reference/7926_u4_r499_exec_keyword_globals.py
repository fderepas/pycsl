r"""Test 7926 -- route #499 (expected FAIL: PROVED at base, REFUSED PYCSL-R499-EXEC-IN-FUNCTION-SCOPE): a MODULE-level `exec("zz = 2", globals={})` runs in another namespace and never binds the real global; `f` claimed 2, CPython raises NameError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


exec("zz = 2", globals={})


#@ ensures \result == 2
def f(n: int) -> int:
    return zz


if __name__ == "__main__":
    try:
        r = f(0)
        if not (r == 2):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
