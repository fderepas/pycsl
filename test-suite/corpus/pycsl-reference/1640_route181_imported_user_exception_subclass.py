r"""Test 1640 - ROUTE #181 (gen #29): an IMPORTED `class MyErr(ValueError)` raised under `except ValueError` PROVED `\result == 0` (CPython 9): route #175's source check did not see the imported class's base.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from multi_file_lib.r181_raising import MyErr


#@ ensures \result == 0
def probe() -> int:
    try:
        raise MyErr()
    except ValueError:
        return 9
    return 0
