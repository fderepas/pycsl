# pycsl-expected: FAIL
#@ requires s == "\n"
#@ ensures \result == 4
def f(s: str) -> int:
    return len(s)
