r"""Test 7545 -- route #476 (expected FAIL): n3_const_rebound_after_main -- driver probe: `K = 0` before the guard, `K = 1` after it, `f` returns `n // K`; CPython ZeroDivisionError. NOT PROVED at 8aaa864ca (the constant is not folded); now REFUSED (PYCSL-R476-REBOUND-AFTER-FRONTIER).
"""
# pycsl-expected: FAIL
K = 0


#@ no_exception \all
def f(n: int) -> int:
    return n // K


if __name__ == "__main__":
    try:
        print(f(1))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)


K = 1
