r"""Test 8297 -- route #510 residual (expected FAIL: PROVED at base, REFUSED PYCSL-R510-TYPE-STATEMENT-NAME-READ; red team 48 probe g900/f9042_cls_from_type_after.py): `from dep import C` where the dependency's class `C` is rebound by `type C = int` in a module-scope `try` body; `C(3).get()` under `ensures \result == 3`; CPython raises TypeError
"""
# pycsl-expected: FAIL
from multi_file_lib.u12_r510_cls import C


#@ ensures \result == 3
def f() -> int:
    c = C(3)
    return c.get()


if __name__ == "__main__":
    try:
        print("result", f())
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
