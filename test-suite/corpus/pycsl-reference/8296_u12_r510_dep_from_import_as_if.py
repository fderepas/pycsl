r"""Test 8296 -- route #510 residual (expected FAIL: PROVED at base, REFUSED PYCSL-R510-TYPE-STATEMENT-NAME-READ; red team 48 probe g900/f9002_from_type_if.py): `from dep import g as h` then `h(3)` under `no_exception \all`, the dependency rebinding `g` by `type g = int` in a module-scope `if` body; CPython raises TypeError
"""
# pycsl-expected: FAIL
from multi_file_lib.u12_r510_if import g as h


#@ no_exception \all
def f() -> int:
    return h(3)


if __name__ == "__main__":
    try:
        print("result", f())
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
