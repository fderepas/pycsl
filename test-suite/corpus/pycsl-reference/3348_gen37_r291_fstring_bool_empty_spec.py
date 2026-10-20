r"""Test 3348 -- route #291 (expected FAIL): `f"{b:}" == f"{x:}"` (empty spec = `format(v, "")` = `str(v)`) PROVED True; CPython 'True' vs '1'.
Now unproven.
"""
# pycsl-expected: FAIL


#@ ensures \result == True
def f() -> bool:
    b = True
    x = 1
    return f"{b:}" == f"{x:}"


if __name__ == "__main__":
    assert f() is False
