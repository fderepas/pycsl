r"""Test 1559 - ROUTE #163 (gen #29): `int(p.s)` with a string field PROVED `no_exception ValueError`; CPython raises.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class P:
    def __init__(self) -> None:
        self.s = "abc"


#@ no_exception ValueError
def probe() -> int:
    p = P()
    return int(p.s)

