r"""Test 8686 -- route #555 (expected FAIL: PROVED at base, REFUSED PYCSL-R545-NONE-OPERAND; red team 52 family F10): `-gn()` of an imported unclaimed `def gn() -> None`; CPython f(1) raises TypeError (bad operand type for unary -)
"""
# pycsl-expected: FAIL
from multi_file_lib.u22_r555_dep import gn


#@ no_exception \all
def f(k: int) -> int:
    return -gn()


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
