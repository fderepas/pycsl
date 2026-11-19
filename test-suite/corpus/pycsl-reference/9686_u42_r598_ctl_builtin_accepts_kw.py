r"""Test 9686 -- route #598 CONTROL, a builtin exception whose constructor DOES accept the keyword (`ImportError('a', name='m')`) and a user `__init__(self, a, code=0)` called within its signature are not refused; `\result == k + 1` needs the handler (expected PASS: PROVED at base bfe0e38fb and at HEAD)
"""
# pycsl-expected: PASS
from typing import Any


#@ requires k >= 0
#@ no_exception \all
#@ ensures \result == k + 1
def f(k: int) -> int:
    r = 0
    try:
        raise ImportError("a", name="m")
    except ImportError:
        r = k + 1
    return r


if __name__ == "__main__":
    print("result", f(4))
