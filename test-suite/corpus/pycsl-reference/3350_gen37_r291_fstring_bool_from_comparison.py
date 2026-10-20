r"""Test 3350 -- route #291 (expected FAIL): red-team fs026::f4: `b = x == 1; f"{b}" == f"{1 if b else 0}"` PROVED True; CPython 'True' vs '1' for x = 1.
Now unproven.
"""
# pycsl-expected: FAIL


#@ ensures \result == True
def f(x: int) -> bool:
    b = x == 1
    return f"{b}" == f"{1 if b else 0}"


if __name__ == "__main__":
    assert f(1) is False
