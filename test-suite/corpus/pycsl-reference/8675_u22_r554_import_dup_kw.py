r"""Test 8675 -- route #554 (expected FAIL: PROVED at base, REFUSED PYCSL-R554-IMPORTED-CALL-SIGNATURE; red team 52 probe bt1204): `g(k, x=k)` of an imported `def g(x: int)`; CPython f(1) raises TypeError (got multiple values for argument 'x')
"""
# pycsl-expected: FAIL
from multi_file_lib.u22_r554_dep import g


#@ no_exception \all
def f(k: int) -> int:
    return g(k, x=k)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
