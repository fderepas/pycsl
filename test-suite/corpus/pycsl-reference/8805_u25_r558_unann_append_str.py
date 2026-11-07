r"""Test 8805 -- route #558 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R558-BYTES-VALUE-KIND; u25 probe beyond red team 53's family): an UNANNOTATED display-bound list `xs = ["a"]; xs.append(bytes(2)); return len(xs[1] + "c")`; CPython TypeError: can't concat str to bytes
"""
# pycsl-expected: FAIL
from typing import List


#@ no_exception \all
def f(k: int) -> int:
    xs = ["a"]
    xs.append(bytes(2))
    return len(xs[1] + "c")


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
