r"""Test 4319 -- gen #37 route #329 (expected FAIL): route #52's run-time-built string `b is c` inside an if-expression PROVED 7 (CPython 0). REFUSED (route #52 refusal).
"""
# pycsl-expected: FAIL
#@ ensures \result == 7
#@ assigns \nothing
def g() -> int:
    a = "a"
    b = a + "b"
    c = "ab"
    return 7 if b is c else 0

if __name__ == "__main__":
    assert g() == 7, g()
