r"""Test 8294 -- route #510 residual (expected FAIL: PROVED at base, REFUSED PYCSL-R510-TYPE-STATEMENT-NAME-READ; red team 48 probe g900/f9000_from_type_after.py): `from dep import g` where the dependency defines `g` and then, at module scope, `type g = int`; the import resolver injects the def; `ensures \result == 3` over `g(3)`; CPython raises TypeError ('typing.TypeAliasType' object is not callable)
"""
# pycsl-expected: FAIL
from multi_file_lib.u12_r510_after import g


#@ ensures \result == 3
def f() -> int:
    return g(3)


if __name__ == "__main__":
    try:
        print("result", f())
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
