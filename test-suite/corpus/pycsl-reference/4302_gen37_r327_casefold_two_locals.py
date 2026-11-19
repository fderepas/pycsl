r"""Test 4302 -- gen #37 route #327 (expected FAIL): `K = 7; k = 3; return K` PROVED `\result == 3` (CPython 7). REFUSED.
"""
# pycsl-expected: FAIL
#@ ensures \result == 3
#@ assigns \nothing
def g() -> int:
    K = 7
    k = 3
    return K

if __name__ == "__main__":
    assert g() == 3, g()
