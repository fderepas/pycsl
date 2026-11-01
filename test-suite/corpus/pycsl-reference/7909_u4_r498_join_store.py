r"""Test 7909 -- route #498 (expected FAIL, store memory model: a Why3 type error at base -- fail closed -- now REFUSED PYCSL-R498-IS-ON-FRESH-VALUE by name): `"".join([s, s]) is "".join([s, s])` claimed True; CPython f('ab') returns False (rt44 j51519)
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model store
from typing import Any, Dict, List, Optional


#@ ensures \result == True
def f(s: str) -> bool:
    return "".join([s, s]) is "".join([s, s])


if __name__ == "__main__":
    try:
        r = f('ab')
        if not (r == True):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
