r"""Test 4285 -- gen #37 route #326 (expected FAIL): `import multi_file_lib.r326pkg` + qualified call, package and module both present: PROVED `g() == 2` (CPython 1). Now FAILS.
"""
# pycsl-expected: FAIL
import multi_file_lib.r326pkg

#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return multi_file_lib.r326pkg.f()

if __name__ == "__main__":
    assert g() == 2, g()
