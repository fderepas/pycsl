r"""Test 3346 -- route #291 (expected FAIL): `b = True; x = 1; f"{b}" == f"{x}"` PROVED True (both lowered to `str_of_int_hash 1`); CPython "True" vs "1" -> False.
Now a bool renders through `str_of_bool_hash`; goal unproven.
"""
# pycsl-expected: FAIL


#@ ensures \result == True
def f() -> bool:
    b = True
    x = 1
    return f"{b}" == f"{x}"


if __name__ == "__main__":
    assert f() is False
