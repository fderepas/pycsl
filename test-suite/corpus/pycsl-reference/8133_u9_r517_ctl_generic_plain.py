r"""Test 8133 -- route #517 (control, expected PASS): a generic def whose type parameter T is never read as a value, beside the module constant `K = 5` its body reads; CPython f(10) returns 2
"""
# pycsl-expected: PASS

K = 5


#@ no_exception \all
#@ ensures \result == n // 5
def f[T](n: int) -> int:
    return n // K


#@ ensures \result == 2
def use() -> int:
    return f(10)


if __name__ == "__main__":
    print("result", use())
