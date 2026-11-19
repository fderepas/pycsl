r"""Test 1618 - ROUTE #175 carrier (gen #29): `Alias = MyErr` (MyErr(ValueError)); `raise Alias()` under `except ValueError` PROVED `\result == 0` on the #175 draft (CPython 9): the source check did not know the alias. Plain-name aliases of exception classes are now resolved.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class MyErr(ValueError):
    pass


Alias = MyErr


#@ ensures \result == 0
def probe() -> int:
    try:
        raise Alias()
    except ValueError:
        return 9
    return 0
