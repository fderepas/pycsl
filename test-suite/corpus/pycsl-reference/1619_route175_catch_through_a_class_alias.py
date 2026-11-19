r"""Test 1619 - ROUTE #175 carrier (gen #29): `Alias = MyErr`; `raise MyErr()` under `except Alias` PROVED `\result == 0` on the #175 draft (CPython 9): the two names are one class in Python and two unrelated Why3 exceptions. A handler naming an alias of the raised class is now refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class MyErr(ValueError):
    pass


Alias = MyErr


#@ ensures \result == 0
def probe() -> int:
    try:
        raise MyErr()
    except Alias:
        return 9
    return 0
