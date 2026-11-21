r"""Test 9684 -- route #597 CONTROL, R597's advice followed: the local that shadowed the exception class is renamed (`T = int`), and `E` is raised by its own name; `\result == k + 1` needs the handler (expected PASS: PROVED at base bfe0e38fb and at HEAD)
"""
# pycsl-expected: PASS
from typing import Any


class E(Exception):
    pass


#@ requires k >= 0
#@ no_exception \all
#@ ensures \result == k + 1
def f(k: int) -> int:
    T = int
    r = 0
    try:
        raise E("a")
    except E:
        r = k + 1
    return r


if __name__ == "__main__":
    print("result", f(4))
