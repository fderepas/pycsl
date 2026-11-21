r"""Test 7925 -- route #499 (expected FAIL, typed memory model: a Why3 type error at base -- fail closed -- now REFUSED PYCSL-R499-EXEC-IN-FUNCTION-SCOPE by name): `exec("(x := 9)")` over a local claimed 9; CPython returns 1
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model typed
from typing import Any, Dict, List, Optional


#@ ensures \result == 9
def f(n: int) -> int:
    x = 1
    exec("(x := 9)")
    return x


if __name__ == "__main__":
    try:
        r = f(0)
        if not (r == 9):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
