r"""Test 5645 -- gen #37 route #399 (expected FAIL): `from builtins import sum`; `sum([1, 2], **{"start": 10}) == 3`; PROVED at base 3b2d2e763 (CPython 13). REFUSED (PYCSL-R379-STARRED-CALL-ARGUMENT).
"""
# pycsl-expected: FAIL
from builtins import sum


#@ ensures \result == 3
def f() -> int:
    return sum([1, 2], **{"start": 10})


if __name__ == "__main__":
    try:
        print("result", f())
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
