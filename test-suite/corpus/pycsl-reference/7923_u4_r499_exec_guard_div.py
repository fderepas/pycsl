r"""Test 7923 -- route #499 (expected FAIL: PROVED at base, REFUSED PYCSL-R499-EXEC-IN-FUNCTION-SCOPE): `d = 0; exec("d = 5"); return 10 // d` claimed `no_exception \\all`; CPython raises ZeroDivisionError (rt44 e51710)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


#@ no_exception \all
def f(n: int) -> int:
    d = 0
    exec("d = 5")
    return 10 // d


if __name__ == "__main__":
    try:
        r = f(0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
