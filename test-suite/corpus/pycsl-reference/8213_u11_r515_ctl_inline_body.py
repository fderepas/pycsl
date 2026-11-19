r"""Test 8213 -- route #515 (control, expected PASS): the body of the refused immediately-invoked lambda written inline as a plain statement, where route #414's bound applies and `requires 0 <= n <= 1000` discharges it; CPython f(5) returns 1
"""
# pycsl-expected: PASS


#@ requires 0 <= n and n <= 1000
#@ no_exception \all
#@ ensures \result == 1
def f(n: int) -> int:
    w = "ab" * n
    return 1


if __name__ == "__main__":
    print(f(5))
