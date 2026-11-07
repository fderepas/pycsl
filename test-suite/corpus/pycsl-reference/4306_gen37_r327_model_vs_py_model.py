r"""Test 4306 -- gen #37 route #327 (expected FAIL): `py_model = 7; model = 3; return py_model` PROVED `\result == 3` (CPython 7). REFUSED.
"""
# pycsl-expected: FAIL
#@ ensures \result == 3
#@ assigns \nothing
def g() -> int:
    py_model = 7
    model = 3
    return py_model

if __name__ == "__main__":
    assert g() == 3, g()
