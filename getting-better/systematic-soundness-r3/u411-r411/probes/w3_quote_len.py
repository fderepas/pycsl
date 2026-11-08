# pycsl-expected: FAIL
#@ requires s == "a\"b"
#@ ensures \result == 6
def f(s: str) -> int:
    return len(s)
