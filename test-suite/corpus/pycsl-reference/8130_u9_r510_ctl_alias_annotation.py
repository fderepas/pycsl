r"""Test 8130 -- route #510 (control, expected PASS): `type Num = int` read only as a TYPE (parameter, return and local annotations); a name never read as a value is not refused; CPython f(3) returns 4
"""
# pycsl-expected: PASS

type Num = int


#@ requires 0 <= n and n <= 1000
#@ no_exception \all
#@ ensures \result == n + 1
def f(n: Num) -> Num:
    k: Num = n + 1
    return k


if __name__ == "__main__":
    print("result", f(3))
