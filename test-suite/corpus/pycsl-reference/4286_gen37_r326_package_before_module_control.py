r"""Test 4286 -- gen #37 route #326 (expected PASS): CONTROL: the package's own contract (`f() == 1`) is the one believed: PROVES (and CPython agrees).
"""
# pycsl-expected: PASS
from multi_file_lib.r326pkg import f

#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return f()

if __name__ == "__main__":
    assert g() == 1, g()
