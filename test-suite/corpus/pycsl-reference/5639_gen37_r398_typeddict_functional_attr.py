r"""Test 5639 -- gen #37 route #398 (expected FAIL): functional `TD = TypedDict("TD", {"a": int})`; `TD(a=1).a` under `no_exception`; PROVED at base 3b2d2e763 (CPython: AttributeError). REFUSED (PYCSL-TC-TYPING-CONSTRUCT-VALUE: the functional form is a typing construct).
"""
# pycsl-expected: FAIL
from typing import TypedDict

TD = TypedDict("TD", {"a": int})


#@ no_exception \all
def f() -> int:
    d = TD(a=1)
    return d.a


if __name__ == "__main__":
    try:
        print("result", f())
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
