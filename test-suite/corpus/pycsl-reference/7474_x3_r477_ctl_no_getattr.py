r"""Test 7474 -- route #477 (control, expected PASS): control -- `from h import g` of a module without `__getattr__` keeps verifying.
"""
# pycsl-expected: PASS
from multi_file_lib.x3_h477d import g


#@ no_exception \all
def f(n: int) -> int:
    return n


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
