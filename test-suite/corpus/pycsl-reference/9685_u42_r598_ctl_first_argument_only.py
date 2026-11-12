r"""Test 9685 -- route #598 CONTROL, R598's advice followed: the keyword is dropped and the extra data bound to a local before the raise (`q = 1; raise ValueError('a')`); `\result == k + q` needs the handler (expected PASS: PROVED at base bfe0e38fb and at HEAD)
"""
# pycsl-expected: PASS
from typing import Any


#@ requires k >= 0
#@ no_exception \all
#@ ensures \result == k + 1
def f(k: int) -> int:
    q = 1
    r = 0
    try:
        raise ValueError("a")
    except ValueError:
        r = k + q
    return r


if __name__ == "__main__":
    print("result", f(4))
