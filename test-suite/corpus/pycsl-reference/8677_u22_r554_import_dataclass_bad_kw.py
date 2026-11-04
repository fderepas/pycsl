r"""Test 8677 -- route #554 (expected FAIL: PROVED at base, REFUSED PYCSL-R554-IMPORTED-CALL-SIGNATURE; red team 52 probe cc1207): `DD(b=k)` of an imported `@dataclass DD: a: int`; CPython f(1) raises TypeError (unexpected keyword argument 'b')
"""
# pycsl-expected: FAIL
from multi_file_lib.u22_r554_dep import DD


#@ no_exception \all
def f(k: int) -> int:
    r = DD(b=k)
    return 1


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
