r"""Test 7927 -- route #499 (expected FAIL: PROVED at base, REFUSED PYCSL-R499-EXEC-IN-FUNCTION-SCOPE): a constant `exec("y = m")` in a class body nested in a function cannot see the function local `m` (class-body exec reads the class namespace and the globals); claimed 1, CPython raises NameError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


#@ ensures \result == 1
def f(n: int) -> int:
    m = 1

    class K:
        exec("y = m")

    return m


if __name__ == "__main__":
    try:
        r = f(0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
