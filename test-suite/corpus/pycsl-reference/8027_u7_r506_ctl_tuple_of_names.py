r"""Test 8027 -- route #506 (control, expected PASS): the tuple display holds only names bound by plain statements (`q = 10 // n; t = (1, q)`), so the division keeps its obligation (`requires n != 0`, `#@ no_exception ZeroDivisionError`); CPython g(5) returns 2)
"""
# pycsl-expected: PASS

#@ requires n != 0
#@ no_exception ZeroDivisionError
#@ ensures \result == 10 // n
def g(n: int) -> int:
    q = 10 // n
    t = (1, q)
    return q


if __name__ == "__main__":
    print("result", g(5))
