r"""Test 4284 -- gen #37 route #326 (expected FAIL): with both `multi_file_lib/r326pkg/__init__.py` (f = 1) and `multi_file_lib/r326pkg.py` (f = 2), CPython loads the PACKAGE; pycsl resolved the module and PROVED `g() == 2`. Now resolves the package: FAILS.
"""
# pycsl-expected: FAIL
from multi_file_lib.r326pkg import f

#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return f()

if __name__ == "__main__":
    assert g() == 2, g()
