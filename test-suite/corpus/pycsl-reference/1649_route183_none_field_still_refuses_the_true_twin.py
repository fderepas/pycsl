r"""Test 1649 - ROUTE #183 control (gen #29): the TRUE twin of 1648 (`c.v == 0` is False in CPython) is not provable either - the opaque `pycsl_none` makes the comparison UNDECIDED rather than wrong, which is the campaign's answer for a value nothing is known about.
"""
# pycsl-expected: FAIL
from typing import Optional
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.v: Optional[int] = None


#@ ensures \result == False
def probe() -> bool:
    c = C()
    return c.v == 0
