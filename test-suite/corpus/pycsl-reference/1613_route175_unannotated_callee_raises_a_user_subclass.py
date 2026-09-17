r"""Test 1613 - ROUTE #175 carrier (gen #29): a method raising `MyErr(ValueError)` with no `#@ raises`, called in `try ... except ValueError` by the caller, PROVED `\result == 0` (CPython 9). The source-level check now reads an unannotated callee`s own `raise` statements.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class MyErr(ValueError):
    pass


class C:
    def __init__(self) -> None:
        self.k = 0

    def go(self) -> int:
        raise MyErr()


#@ ensures \result == 0
def probe() -> int:
    c = C()
    try:
        c.go()
    except ValueError:
        return 9
    return 0
