r"""Test 8662 -- route #549 (expected FAIL: PROVED at base, REFUSED PYCSL-R549-NONE-ARGUMENT; red team 52 probe bn1203): `m.g(None)` through `import ... as m`; CPython f(1) raises TypeError
"""
# pycsl-expected: FAIL
import multi_file_lib.u22_r549_dep as m


#@ no_exception \all
def f(k: int) -> int:
    return m.g(None)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
