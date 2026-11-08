r"""Test 8170 -- route #518 (control, expected PASS): a module lambda whose default is the plain constant name and whose BODY holds a walrus (binding the lambda's own local); CPython returns 5
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

K = 5
_l = lambda a=K: (b := a + 1)


#@ ensures \result == 5
def f() -> int:
    return K


if __name__ == "__main__":
    try:
        r = f()
        if not (r == 5):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
