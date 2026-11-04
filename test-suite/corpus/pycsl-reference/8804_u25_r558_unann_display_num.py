r"""Test 8804 -- route #558 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R558-BYTES-VALUE-KIND; u25 probe beyond red team 53's family): an UNANNOTATED display `xs = [1, bytes(2)]; return xs[1] + 1`; CPython TypeError: can't concat int to bytes
"""
# pycsl-expected: FAIL
from typing import List


#@ no_exception \all
def f(k: int) -> int:
    xs = [1, bytes(2)]
    return xs[1] + 1


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
