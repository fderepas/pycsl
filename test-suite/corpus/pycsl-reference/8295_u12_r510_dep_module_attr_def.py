r"""Test 8295 -- route #510 residual (expected FAIL: PROVED at base, REFUSED PYCSL-R510-TYPE-STATEMENT-NAME-READ; red team 48 probe g900/f9001_mod_type_after.py): `import dep as d` then `d.g(3)` under `no_exception \all`, the dependency rebinding `g` by a module-scope `type g = int`; CPython raises TypeError
"""
# pycsl-expected: FAIL
import multi_file_lib.u12_r510_after as d


#@ no_exception \all
def f() -> int:
    return d.g(3)


if __name__ == "__main__":
    try:
        print("result", f())
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
