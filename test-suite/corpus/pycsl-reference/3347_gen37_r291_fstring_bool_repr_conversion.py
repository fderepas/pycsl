r"""Test 3347 -- route #291 (expected FAIL): `f"{b!r}" == f"{x!r}"` (b = True, x = 1) PROVED True (`pycsl_format_r_i_h` keyed on the int model); CPython 'True' vs '1'.
Now the bool operand gets its own `b` symbol; goal unproven.
"""
# pycsl-expected: FAIL


#@ ensures \result == True
def f() -> bool:
    b = True
    x = 1
    return f"{b!r}" == f"{x!r}"


if __name__ == "__main__":
    assert f() is False
