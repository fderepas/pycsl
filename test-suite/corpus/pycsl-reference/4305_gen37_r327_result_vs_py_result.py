r"""Test 4305 -- gen #37 route #327 (expected FAIL): `result = 7; py_result = 3; return result`: the keyword prefix makes `result` -> `py_result`, and `\result == 3` PROVED (CPython 7). REFUSED.
"""
# pycsl-expected: FAIL
#@ ensures \result == 3
#@ assigns \nothing
def g() -> int:
    result = 7
    py_result = 3
    return result

if __name__ == "__main__":
    assert g() == 3, g()
