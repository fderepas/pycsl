r"""Test 7267 -- route #466 (red team 38, expected FAIL: PROVED at base, REFUSED): `h.g(n)` where the module binds `g` only under `if False:`; CPython AttributeError.
"""
# pycsl-expected: FAIL
import multi_file_lib.x1_h466b as h


#@ no_exception \all
def f(n: int) -> int:
    return h.g(n)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
