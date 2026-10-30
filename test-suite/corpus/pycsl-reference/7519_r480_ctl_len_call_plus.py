r"""Test 7519 -- route #480 (expected PASS): CONTROL -- `len(a) + 1` claiming `\result == 3` (a CALL of a builtin is not its name used as a value). PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import List


#@ ensures \result == 3
#@ no_exception \all
def f(n: int) -> int:
    a = [1, 2]
    return len(a) + 1


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
