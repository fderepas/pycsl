r"""Test 3349 -- route #291 (expected FAIL): `f"{True}" == f"{1}"` PROVED True; CPython False.
Now unproven.
"""
# pycsl-expected: FAIL


#@ ensures \result == True
def f() -> bool:
    return f"{True}" == f"{1}"


if __name__ == "__main__":
    assert f() is False
