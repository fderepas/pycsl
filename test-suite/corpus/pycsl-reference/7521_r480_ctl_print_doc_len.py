r"""Test 7521 -- route #480 (expected PASS): CONTROL -- `len(print.__doc__) + n` under `no_exception \all` (an existing attribute of a builtin, consumed by `len`). PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import List


#@ no_exception \all
def f(n: int) -> int:
    return len(print.__doc__) + n


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
