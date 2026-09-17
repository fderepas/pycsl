r"""Test 1647 - ROUTE #182 carrier (gen #29): the same helper called with -1 inside `try ... except ValueError: return 9` PROVED `\result == 0` (CPython 9).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


def shift(x: int) -> int:
    return 1 << x


#@ ensures \result == 0
def probe() -> int:
    try:
        v = shift(-1)
    except ValueError:
        return 9
    return 0
