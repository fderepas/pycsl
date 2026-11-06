r"""Test 9147 -- lvD3 control (expected FAIL, refused before and after): a nested function reading
the hashed local. The lift refusal (captured name) holds; listed so a future lift cannot reopen F4 silently.
"""
# pycsl-expected: FAIL
from __future__ import annotations


#@ no_exception \all
#@ assigns \nothing
def f(x: int) -> int:
    name = x
    name = "abc"

    def g() -> int:
        return name + 1
    return g()


if __name__ == "__main__":
    try:
        print("result", f(3))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
