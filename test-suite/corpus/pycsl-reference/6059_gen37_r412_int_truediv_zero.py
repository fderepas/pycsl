r"""Test 6059 -- gen #37 route #412 (expected FAIL): int TRUE division `a / b` with no `b != 0` under `no_exception \all`, f(1, 0) (CPython ZeroDivisionError; PROVED at base 4431ef86f: the `float_truediv_op` bridge was the one int division path not wrapped by the `("binop", "/")` row).
"""
# pycsl-expected: FAIL
#@ no_exception \all
def f(a: int, b: int) -> float:
    return a / b


if __name__ == "__main__":
    try:
        r = f(1, 0)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
