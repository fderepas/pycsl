r"""Test 1609 - ROUTE #175 (gen #29): `class Sub(Base)` raised and caught by `except Base` PROVED `\result == 0` (CPython 9).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class Base(Exception):
    pass


class Sub(Base):
    pass


#@ ensures \result == 0
def probe() -> int:
    try:
        raise Sub()
    except Base:
        return 9
    return 0
